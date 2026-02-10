import warnings
import pandas as pd
from typing import Dict
from functools import cached_property
from requests import Session
from io import BytesIO
from core import Market
from utils import DuckDBManager


class CNMarket(Market):
    """A股市场"""

    def __init__(self, conf: Dict):
        super().__init__()
        self.db_path: str = conf.get("DB_PATH", ":memory:")

    def _spa_stock_info_from_szse(self) -> pd.DataFrame:
        with Session() as s:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                return (
                    pd.read_excel(
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
                    .rename(
                        columns={"板块": "board", "A股代码": "code", "A股简称": "name"}
                    )
                    .assign(
                        exchange="SZ",
                        code=lambda df: df["code"]
                        .astype(str)
                        .str.split(".", expand=True)
                        .iloc[:, 0]
                        .str.zfill(6)
                        .str.replace("000nan", ""),
                        board=lambda df: df["board"].replace(
                            {"主板": "A-shares", "创业板": "STAR"}
                        ),
                    )[["exchange", "code", "name", "board"]]
                )

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
                .assign(board="A-shares")
            )[["code", "name", "board"]]
            tmp_df_kcb = (
                pd.DataFrame(
                    s.get(
                        "https://query.sse.com.cn/sseQuery/commonQuery.do",
                        params=params | {"STOCK_TYPE": "8"},
                    ).json()["result"]
                )
                .rename(columns={"A_STOCK_CODE": "code", "COMPANY_ABBR": "name"})
                .assign(board="ChiNext")
            )[["code", "name", "board"]]
        return pd.concat([tmp_df_a, tmp_df_kcb], ignore_index=True).assign(
            exchange="SH"
        )[["exchange", "code", "name", "board"]]

    def spa_stock_info(self) -> str:
        table_name = "SECURITY"
        # stock_sz = Market.fetch_stock_from_eastmoney(
        #     "SZSE",
        # ).assign(
        #     exchange="SZ",
        #     code=lambda df: df["code"]
        #     .astype(str)
        #     .str.split(".", expand=True)
        #     .iloc[:, 0]
        #     .str.zfill(6)
        #     .str.replace("000nan", ""),
        # )
        stock_sz = self._spa_stock_info_from_szse()
        # stock_sh = Market.fetch_stock_from_eastmoney("SSE").assign(exchange="SH")
        stock_sh = self._spa_stock_info_from_sse()
        if DuckDBManager.table_exists(table_name, self.db_path):
            DuckDBManager.execute(
                f"DELETE FROM {table_name} WHERE EXCHANGE IN(?,?);",
                self.db_path,
                params=("SH", "SZ"),
            )
        DuckDBManager.insert_df(
            table_name,
            pd.concat([stock_sz, stock_sh], ignore_index=True),
            self.db_path,
        )
        return table_name

    @property
    def trading_hours(self):
        print("CNMarket: Getting trading hours...")

    @cached_property
    def security_list(self):
        return DuckDBManager.query_df(
            sql="SELECT * FROM security WHERE EXCHANGE IN(?,?);",
            db_path=self.db_path,
            params=("SH", "SZ"),
        )
