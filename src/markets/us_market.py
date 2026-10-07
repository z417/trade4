import asyncio
from typing import Optional
import pandas as pd
from core import Market, DatabaseService
from utils.async_fetchers import fetch_stock_from_sina_async
from utils import logger


def USMarket(conf, db: Optional[DatabaseService] = None) -> Market:
    """
    美股市场闭包工厂：遵循 Market(NamedTuple) 契约，全异步实现
    """
    db_path: str = conf.database_path

    async def spa_stock_info() -> str:
        try:
            raw_df = await fetch_stock_from_sina_async("US")
            if not raw_df.empty:
                us_df = raw_df.assign(
                    exchange="US",
                    symbol=lambda df: df["code"] + ".US",
                )[["symbol", "exchange", "code", "name", "board"]]
                if db is not None:
                    await db.insert_df("SECURITY", us_df, if_exists="append")
                else:
                    import duckdb
                    def _write():
                        with duckdb.connect(db_path) as conn:
                            conn.register("__temp_us", us_df)
                            conn.execute("INSERT INTO SECURITY SELECT * FROM __temp_us;")
                            conn.unregister("__temp_us")
                    await asyncio.to_thread(_write)
        except Exception as e:
            logger.warning(f"美股标的抓取失败: {e}")
        return "SECURITY"

    async def get_trading_hours() -> str:
        return "09:30-16:00 (America/New_York)"

    async def get_security_list() -> pd.DataFrame:
        sql = "SELECT * FROM SECURITY WHERE exchange = 'US';"
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


__all__ = ["USMarket"]
