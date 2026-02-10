import duckdb
from typing import Optional, Union, Literal
import pandas as pd


class DuckDBManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path

    def __enter__(self) -> duckdb.DuckDBPyConnection:
        self.conn = duckdb.connect(self.db_path)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "conn") and self.conn:
            self.conn.close()

    @staticmethod
    def _get_connection(db_path: str) -> duckdb.DuckDBPyConnection:
        """内部辅助: 创建临时连接(用于静态方法)"""
        return duckdb.connect(db_path)

    @staticmethod
    def execute(
        sql: str, db_path: str = ":memory:", params: Optional[Union[tuple, dict]] = None
    ) -> None:
        """
        执行非查询 SQL(如 CREATE, INSERT, DELETE)
        """
        with DuckDBManager._get_connection(db_path) as conn:
            conn.execute(sql, params)

    @staticmethod
    def query_df(
        sql: str, db_path: str = ":memory:", params: Optional[Union[tuple, dict]] = None
    ) -> pd.DataFrame:
        """
        执行查询并返回 pandas DataFrame
        """
        with DuckDBManager._get_connection(db_path) as conn:
            return conn.execute(sql, params).fetchdf()

    @staticmethod
    def insert_df(
        table_name: str,
        df: pd.DataFrame,
        db_path: str = ":memory:",
        if_exists: Literal["append", "replace", "append", "fail"] = "append",
    ) -> None:
        """
        将 DataFrame 写入 DuckDB 表
        if_exists:
          - 'replace': 先 DROP 再 CREATE
          - 'append': 直接插入（要求表结构一致）
          - 'fail': 表存在则报错
        """
        with DuckDBManager._get_connection(db_path) as conn:
            if if_exists == "replace":
                conn.register("__temp_df", df)  # 注册 DataFrame 为临时视图
                conn.execute(
                    f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM __temp_df"
                )
                conn.unregister("__temp_df")
            elif if_exists == "fail":
                if DuckDBManager.table_exists(table_name, db_path):
                    raise ValueError(f"Table {table_name} already exists.")
                conn.register("__temp_df", df)
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM __temp_df")
                conn.unregister("__temp_df")
            elif if_exists == "append":
                # DuckDB 支持直接 INSERT FROM df
                conn.register("__temp_df", df)
                try:
                    conn.execute(f"INSERT INTO {table_name} SELECT * FROM __temp_df")
                except duckdb.CatalogException:
                    conn.execute(
                        f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM __temp_df"
                    )
                    conn.execute(f"INSERT INTO {table_name} SELECT * FROM __temp_df")
                conn.unregister("__temp_df")
            else:
                raise ValueError("if_exists must be 'replace', 'append', or 'fail'")

    @staticmethod
    def table_exists(table_name: str, db_path: str = ":memory:") -> bool:
        """检查表是否存在"""
        with DuckDBManager._get_connection(db_path) as conn:
            result = conn.execute(
                """
                SELECT COUNT(1) 
                FROM information_schema.tables 
                WHERE table_name = ?
            """,
                [table_name],
            ).fetchone()
            if result:
                return result[0] > 0
        return False

    @staticmethod
    def export_to_parquet(
        table_name: str, file_path: str, db_path: str = ":memory:"
    ) -> None:
        """导出表为 Parquet 文件"""
        with DuckDBManager._get_connection(db_path) as conn:
            conn.execute(f"COPY {table_name} TO '{file_path}' (FORMAT PARQUET);")
