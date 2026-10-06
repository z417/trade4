import warnings
import pandas as pd
from functools import cached_property
from requests import Session
from io import BytesIO
from core import Market
from utils import DuckDBManager


class CNMarket(Market):
    """A股市场"""

    def __init__(self, conf):
        super().__init__()
        self.db_path: str = conf.database_path

    def _spa_stock_info_from_szse(self) -> pd.DataFrame:
        with Session() as s:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                raw_df = pd.read_excel(
                    BytesIO(
                        s.get(
                            "https://www.szse.cn/api/report/ShowReport",
                            params={
                                "SHOWTYPE": "xlsx",
                                "CATALOGID": "1110",
                                "TABKEY": "tab1",
                                "random": "0.6935816432433362",
                            },
                            timeout=15,
                        ).content
                    ),
                    usecols=["板块", "A股代码", "A股简称"],
                )
                df = (
                    raw_df.rename(columns={"板块": "board", "A股代码": "code", "A股简称": "name"})
                    .assign(
                        exchange="SZ",
                        code=lambda d: d["code"]
                        .astype(str)
                        .str.split(".", expand=True)
                        .iloc[:, 0]
                        .str.zfill(6)
                        .str.replace("000nan", ""),
                        board=lambda d: d["board"].replace({"主板": "Main", "创业板": "ChiNext"}),
                    )
                )
                df = df[df["code"].str.len() == 6].copy()
                df["symbol"] = df["code"] + ".SZ"
                return df[["symbol", "exchange", "code", "name", "board"]]

    def _spa_stock_info_from_sse(self) -> pd.DataFrame:
        with Session() as s:
            s.headers.update(
                {
                    "Host": "query.sse.com.cn",
                    "Pragma": "no-cache",
                    "Referer": "https://www.sse.com.cn/assortment/stock/list/share/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                }
            )
            params = {
                "REG_PROVINCE": "",
                "CSRC_CODE": "",
                "STOCK_CODE": "",
                "sqlId": "COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L",
                "COMPANY_STATUS": "2,4,5,7,8",
                "type": "inParams",
                "isPagination": "true",
                "pageHelp.cacheSize": "1",
                "pageHelp.beginPage": "1",
                "pageHelp.pageSize": "10000",
                "pageHelp.pageNo": "1",
                "pageHelp.endPage": "1",
            }
            tmp_df_a = (
                pd.DataFrame(
                    s.get(
                        "https://query.sse.com.cn/sseQuery/commonQuery.do",
                        params=params | {"STOCK_TYPE": "1"},
                    ).json()["result"]
                )
                .rename(columns={"A_STOCK_CODE": "code", "COMPANY_ABBR": "name"})
                .assign(board="Main")
            )[["code", "name", "board"]]
            tmp_df_kcb = (
                pd.DataFrame(
                    s.get(
                        "https://query.sse.com.cn/sseQuery/commonQuery.do",
                        params=params | {"STOCK_TYPE": "8"},
                    ).json()["result"]
                )
                .rename(columns={"A_STOCK_CODE": "code", "COMPANY_ABBR": "name"})
                .assign(board="STAR")
            )[["code", "name", "board"]]
        df = pd.concat([tmp_df_a, tmp_df_kcb], ignore_index=True).assign(exchange="SH")
        df["code"] = df["code"].astype(str).str.zfill(6)
        df = df[df["code"].str.len() == 6].copy()
        df["symbol"] = df["code"] + ".SH"
        return df[["symbol", "exchange", "code", "name", "board"]]

    def spa_stock_info(self) -> str:
        stock_sz = self._spa_stock_info_from_szse()
        stock_sh = self._spa_stock_info_from_sse()
        combined_df = pd.concat([stock_sz, stock_sh], ignore_index=True)
        return self._save_securities_to_db(combined_df, ("SH", "SZ"))

    @property
    def trading_hours(self):
        """A股交易时间：9:30-11:30, 13:00-15:00 (北京时间)"""
        return {
            "pre_market": ("09:15", "09:25"),
            "morning": ("09:30", "11:30"),
            "afternoon": ("13:00", "15:00"),
            "timezone": "Asia/Shanghai",
        }

    @cached_property
    def security_list(self):
        return DuckDBManager.query_df(
            sql="SELECT * FROM SECURITY WHERE exchange IN (?, ?);",
            db_path=self.db_path,
            params=("SH", "SZ"),
        )
