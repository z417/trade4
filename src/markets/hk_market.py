import asyncio
from io import BytesIO
from typing import Optional
import httpx
import pandas as pd
from core import Market, DatabaseService
from utils import logger


def HKMarket(conf, db: Optional[DatabaseService] = None) -> Market:
    """
    港股市场闭包工厂：遵循 Market(NamedTuple) 契约，全异步实现
    """
    db_path: str = conf.database_path

    async def _fetch_hkex() -> pd.DataFrame:
        url = "https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/services/trading/securities/securitieslists/ListOfSecurities_c.xlsx"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    tmp_df = (
                        pd.read_excel(
                            BytesIO(resp.content),
                            header=2,
                            usecols=["股份代號", "股份名稱", "分類", "次分類", "交易貨幣"],
                        )
                        .query("分類=='股本' and 交易貨幣=='HKD' and 次分類 in ['股本證券(主板)', '股本證券(創業板)']")
                        .rename(
                            columns={
                                "股份代號": "code",
                                "股份名稱": "name",
                                "次分類": "board",
                            }
                        )
                        .assign(
                            board=lambda df: df["board"].replace({"股本證券(主板)": "Main", "股本證券(創業板)": "GEM"}),
                            exchange="HK",
                            code=lambda df: df["code"].astype(str).str.zfill(5),
                            symbol=lambda df: df["code"].astype(str).str.lstrip("0") + ".HK",
                        )[["symbol", "exchange", "code", "name", "board"]]
                    )
                    return tmp_df
        except Exception as e:
            logger.warning(f"从港交所拉取标的失败: {e}")
        return pd.DataFrame()

    async def spa_stock_info() -> str:
        df = await _fetch_hkex()
        if not df.empty:
            if db is not None:
                await db.insert_df("SECURITY", df, if_exists="append")
            else:
                import duckdb
                def _write():
                    with duckdb.connect(db_path) as conn:
                        conn.register("__temp_hk", df)
                        conn.execute("INSERT INTO SECURITY SELECT * FROM __temp_hk;")
                        conn.unregister("__temp_hk")
                await asyncio.to_thread(_write)
        return "SECURITY"

    async def get_trading_hours() -> str:
        return "09:30-12:00, 13:00-16:00 (Asia/Hong_Kong)"

    async def get_security_list() -> pd.DataFrame:
        sql = "SELECT * FROM SECURITY WHERE exchange = 'HK';"
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


__all__ = ["HKMarket"]
