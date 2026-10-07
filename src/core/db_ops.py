from typing import Protocol, Any, Coroutine, NamedTuple, Literal, LiteralString
import pandas as pd


class ExecuteSqlFunc(Protocol):
    def __call__(self, sql: LiteralString, params: tuple | dict | None = None) -> Coroutine[Any, Any, None]: ...


class QueryDfFunc(Protocol):
    def __call__(self, sql: str, params: tuple | dict | None = None) -> Coroutine[Any, Any, pd.DataFrame]: ...


class InsertDfFunc(Protocol):
    def __call__(
        self, table_name: str, df: pd.DataFrame, if_exists: Literal["append", "replace", "fail"] = "append"
    ) -> Coroutine[Any, Any, None]: ...


class CloseDbFunc(Protocol):
    def __call__(self) -> Coroutine[Any, Any, None]: ...


class DatabaseService(NamedTuple):
    """数据库操作不可变记录 (Immutable Record)"""

    execute_sql: ExecuteSqlFunc
    query_df: QueryDfFunc
    insert_df: InsertDfFunc
    close: CloseDbFunc  # 用于优雅停机 (await db.close())


__all__ = ["DatabaseService"]
