import asyncio
from io import BytesIO
import warnings
from typing import Optional
import httpx
import pandas as pd
from core import Market, DatabaseService
from utils import logger


def CNMarket(conf, db: Optional[DatabaseService] = None) -> Market:
    """
    A股市场闭包工厂：遵循 Market(NamedTuple) 契约，全异步实现
    """
    db_path: str = conf.database_path

    async def _fetch_szse() -> pd.DataFrame:
        """异步拉取深交所标的"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    "https://www.szse.cn/api/report/ShowReport",
                    params={
                        "SHOWTYPE": "xlsx",
                        "CATALOGID": "1110",
                        "TABKEY": "tab1",
                        "random": "0.6935816432433362",
                    },
                )
                if resp.status_code == 200:
                    with warnings.catch_warnings(record=True):
                        warnings.simplefilter("always")
                        raw_df = pd.read_excel(
                            BytesIO(resp.content),
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
        except Exception as e:
            logger.warning(f"从深交所拉取标的失败: {e}")
        return pd.DataFrame()

    async def _fetch_sse() -> pd.DataFrame:
        """异步拉取上交所标的"""
        headers = {
            "Host": "query.sse.com.cn",
            "Pragma": "no-cache",
            "Referer": "https://www.sse.com.cn/assortment/stock/list/share/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
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
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                r1 = await client.get(
                    "https://query.sse.com.cn/sseQuery/commonQuery.do",
                    params=params | {"STOCK_TYPE": "1"},
                )
                r2 = await client.get(
                    "https://query.sse.com.cn/sseQuery/commonQuery.do",
                    params=params | {"STOCK_TYPE": "8"},
                )
                tmp_df_a = (
                    pd.DataFrame(r1.json().get("result", []))
                    .rename(columns={"A_STOCK_CODE": "code", "COMPANY_ABBR": "name"})
                    .assign(board="Main")
                )[["code", "name", "board"]]
                tmp_df_kcb = (
                    pd.DataFrame(r2.json().get("result", []))
                    .rename(columns={"A_STOCK_CODE": "code", "COMPANY_ABBR": "name"})
                    .assign(board="STAR")
                )[["code", "name", "board"]]
                df = pd.concat([tmp_df_a, tmp_df_kcb], ignore_index=True).assign(exchange="SH")
                df["code"] = df["code"].astype(str).str.zfill(6)
                df = df[df["code"].str.len() == 6].copy()
                df["symbol"] = df["code"] + ".SH"
                return df[["symbol", "exchange", "code", "name", "board"]]
        except Exception as e:
            logger.warning(f"从上交所拉取标的失败: {e}")
        return pd.DataFrame()

    async def spa_stock_info() -> str:
        """抓取并入库市场标的信息，返回表名"""
        stock_sz, stock_sh = await asyncio.gather(_fetch_szse(), _fetch_sse())
        combined_df = pd.concat([stock_sz, stock_sh], ignore_index=True)
        if not combined_df.empty:
            if db is not None:
                await db.insert_df("SECURITY", combined_df, if_exists="append")
            else:
                import duckdb
                def _write():
                    with duckdb.connect(db_path) as conn:
                        conn.register("__temp_sec", combined_df)
                        conn.execute("CREATE TABLE IF NOT EXISTS SECURITY AS SELECT * FROM __temp_sec WHERE 1=0;")
                        conn.execute("INSERT INTO SECURITY SELECT * FROM __temp_sec;")
                        conn.unregister("__temp_sec")
                await asyncio.to_thread(_write)
        return "SECURITY"

    async def get_trading_hours() -> str:
        """A股交易时间：9:30-11:30, 13:00-15:00 (北京时间)"""
        return "09:30-11:30, 13:00-15:00 (Asia/Shanghai)"

    async def get_security_list() -> pd.DataFrame:
        """获取当前市场所有标的列表"""
        sql = "SELECT * FROM SECURITY WHERE exchange IN ('SH', 'SZ');"
        if db is not None:
            return await db.query_df(sql)
        import duckdb
        def _read():
            with duckdb.connect(db_path) as conn:
                try:
                    return conn.execute(sql).fetchdf()
                except Exception:
                    return pd.DataFrame()
        return await asyncio.to_thread(_read)

    return Market(
        spa_stock_info=spa_stock_info,
        get_trading_hours=get_trading_hours,
        get_security_list=get_security_list,
    )


__all__ = ["CNMarket"]
