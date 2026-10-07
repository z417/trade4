import asyncio
import duckdb
import pandas as pd
from typing import Optional, Union, Literal, LiteralString
from core import DatabaseService
from utils import logger


async def create_duckdb_service(db_path: str) -> DatabaseService:
    """
    DuckDB 服务工厂：建立长链接，封存连接状态，返回异步函数集。
    """
    logger.info(f"正在初始化 DuckDB 连接: {db_path}")
    conn = duckdb.connect(db_path)
    write_lock = asyncio.Lock()

    def _sync_execute(sql: LiteralString, params: Optional[Union[tuple, dict]]) -> None:
        conn.execute(sql, params)

    def _sync_query_df(sql: str, params: Optional[Union[tuple, dict]]) -> pd.DataFrame:
        return conn.execute(sql, params).fetchdf()

    def _sync_insert_df(table_name: str, df: pd.DataFrame, if_exists: Literal["append", "replace", "fail"]) -> None:
        conn.register("__temp_df", df)
        try:
            if if_exists == "replace":
                conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM __temp_df")
            else:
                try:
                    conn.execute(f"INSERT INTO {table_name} SELECT * FROM __temp_df")
                except duckdb.CatalogException:
                    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM __temp_df")
        finally:
            conn.unregister("__temp_df")

    def _sync_close() -> None:
        conn.close()

    async def execute_sql(sql: LiteralString, params: Optional[Union[tuple, dict]] = None) -> None:
        async with write_lock:
            await asyncio.to_thread(_sync_execute, sql, params)

    async def query_df(sql: str, params: Optional[Union[tuple, dict]] = None) -> pd.DataFrame:
        return await asyncio.to_thread(_sync_query_df, sql, params)

    async def insert_df(
        table_name: str, df: pd.DataFrame, if_exists: Literal["append", "replace", "fail"] = "append"
    ) -> None:
        async with write_lock:
            await asyncio.to_thread(_sync_insert_df, table_name, df, if_exists)

    async def close() -> None:
        await asyncio.to_thread(_sync_close)
        logger.info("DuckDB 连接已安全释放。")

    return DatabaseService(
        execute_sql=execute_sql,
        query_df=query_df,
        insert_df=insert_df,
        close=close,
    )


__all__ = ["create_duckdb_service"]
