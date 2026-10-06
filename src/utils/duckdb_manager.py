from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Literal, Optional, Sequence, Union
import duckdb
import pandas as pd

DbPathType = Union[str, Path]
IfExistsMode = Literal["append", "replace", "fail"]


class DuckDBManager:
    """
    DuckDB 嵌入式数据库管理器

    架构设计:
    - 双模支持: 既支持面向对象实例调用 (db.query_df)，又支持类方法便捷调用 (DuckDBManager.query_df)
    - 资源安全: 统一采用 contextmanager 上下文生命周期，杜绝文件锁占用与泄露
    - 内存自洽: 对 ':memory:' 自动维护活跃单例会话，解决多调用间内存库无法共享的经典陷阱
    - 模式安全: 自动处理父级目录创建、大小写不敏感元数据检索与视图隔离注销
    """

    _shared_memory_instance: Optional["DuckDBManager"] = None

    def __init__(self, db_path: DbPathType = ":memory:"):
        self.db_path = self._normalize_path(db_path)
        # 对内存模式保持长连接以持久化会话；文件模式按需建立连接
        self._conn: Optional[duckdb.DuckDBPyConnection] = (
            duckdb.connect(":memory:") if self.db_path == ":memory:" else None
        )

    @staticmethod
    def _normalize_path(db_path: DbPathType) -> str:
        """规范化路径并自动递归创建父目录"""
        if str(db_path) == ":memory:":
            return ":memory:"
        path = Path(db_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    @contextmanager
    def connect(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """连接上下文管理器，自动管理连接生命周期与异常关闭"""
        if self._conn is not None:
            yield self._conn
        else:
            conn = duckdb.connect(self.db_path)
            try:
                yield conn
            finally:
                conn.close()

    def __enter__(self) -> duckdb.DuckDBPyConnection:
        if self._conn is not None:
            return self._conn
        self._ctx_conn = duckdb.connect(self.db_path)
        return self._ctx_conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "_ctx_conn") and self._ctx_conn:
            self._ctx_conn.close()
            self._ctx_conn = None

    @classmethod
    def _resolve_instance(cls, db_path: DbPathType) -> "DuckDBManager":
        """内部路由: 获取对应路径的管理器实例"""
        if str(db_path) == ":memory:":
            if cls._shared_memory_instance is None:
                cls._shared_memory_instance = cls(":memory:")
            return cls._shared_memory_instance
        return cls(db_path)

    # ==========================
    # 实例方法 (面向对象优雅调用)
    # ==========================

    def execute_query(
        self,
        sql: str,
        params: Optional[Union[Sequence, dict]] = None,
        conn: Optional[duckdb.DuckDBPyConnection] = None,
    ) -> None:
        """执行非查询 SQL (如 DDL, UPDATE, DELETE)"""
        if conn is not None:
            conn.execute(sql, params)
            return

        with self.connect() as local_conn:
            local_conn.execute(sql, params)

    def query_dataframe(
        self,
        sql: str,
        params: Optional[Union[Sequence, dict]] = None,
        conn: Optional[duckdb.DuckDBPyConnection] = None,
        temp_views: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        执行查询并返回 pandas.DataFrame

        :param sql: SQL 语句
        :param params: 参数绑定
        :param conn: 外部传入的连接
        :param temp_views: 临时注册并在执行后自动注销的 DataFrame 字典，如 {"df_name": df}
        """
        def _exec(c: duckdb.DuckDBPyConnection):
            if temp_views:
                for v_name, v_df in temp_views.items():
                    c.register(v_name, v_df)
            try:
                return c.execute(sql, params).fetchdf()
            finally:
                if temp_views:
                    for v_name in temp_views.keys():
                        try:
                            c.unregister(v_name)
                        except Exception:
                            pass

        if conn is not None:
            return _exec(conn)

        with self.connect() as local_conn:
            return _exec(local_conn)

    # 实例方法别名统一
    query_df = query_dataframe

    def insert_dataframe(
        self,
        table_name: str,
        df: pd.DataFrame,
        if_exists: IfExistsMode = "append",
        conn: Optional[duckdb.DuckDBPyConnection] = None,
    ) -> None:
        """
        将 DataFrame 写入 DuckDB 表

        :param table_name: 目标表名
        :param df: 数据 DataFrame
        :param if_exists: 'replace'(覆盖), 'append'(追加), 'fail'(已存在抛异常)
        :param conn: 可选的外层事务连接
        """
        if if_exists not in ("append", "replace", "fail"):
            raise ValueError(f"if_exists 必须为 'append', 'replace' 或 'fail', 当前为: {if_exists}")

        def _do_insert(c: duckdb.DuckDBPyConnection):
            view_name = f"__temp_view_{abs(hash(table_name))}"
            c.register(view_name, df)
            try:
                safe_table = f'"{table_name}"'
                if if_exists == "replace":
                    c.execute(f"CREATE OR REPLACE TABLE {safe_table} AS SELECT * FROM {view_name}")
                elif if_exists == "fail":
                    if self.has_table(table_name, conn=c):
                        raise ValueError(f"表 '{table_name}' 已存在。")
                    c.execute(f"CREATE TABLE {safe_table} AS SELECT * FROM {view_name}")
                elif if_exists == "append":
                    try:
                        c.execute(f"INSERT INTO {safe_table} SELECT * FROM {view_name}")
                    except duckdb.CatalogException:
                        c.execute(f"CREATE TABLE {safe_table} AS SELECT * FROM {view_name}")
            finally:
                c.unregister(view_name)

        if conn is not None:
            _do_insert(conn)
        else:
            with self.connect() as local_conn:
                _do_insert(local_conn)

    def has_table(
        self,
        table_name: str,
        conn: Optional[duckdb.DuckDBPyConnection] = None,
    ) -> bool:
        """大小写不敏感检查表是否存在"""
        sql = "SELECT 1 FROM information_schema.tables WHERE lower(table_name) = lower(?) LIMIT 1"
        if conn is not None:
            return conn.execute(sql, [table_name]).fetchone() is not None

        with self.connect() as local_conn:
            return local_conn.execute(sql, [table_name]).fetchone() is not None

    def get_column_names(
        self,
        table_name: str,
        conn: Optional[duckdb.DuckDBPyConnection] = None,
    ) -> List[str]:
        """获取表的列名列表 (保持原有定义顺序)"""
        sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE lower(table_name) = lower(?) 
            ORDER BY ordinal_position
        """
        if conn is not None:
            rows = conn.execute(sql, [table_name]).fetchall()
            return [r[0] for r in rows]

        with self.connect() as local_conn:
            rows = local_conn.execute(sql, [table_name]).fetchall()
            return [r[0] for r in rows]

    def export_parquet(
        self,
        table_name: str,
        file_path: DbPathType,
        conn: Optional[duckdb.DuckDBPyConnection] = None,
    ) -> None:
        """导出表至 Parquet 文件"""
        target_path = Path(file_path).resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        sql = f"COPY \"{table_name}\" TO '{target_path.as_posix()}' (FORMAT PARQUET);"

        if conn is not None:
            conn.execute(sql)
            return

        with self.connect() as local_conn:
            local_conn.execute(sql)

    # ==========================
    # 快捷类方法 (100% 保持历史调用兼容)
    # ==========================

    @classmethod
    def execute(
        cls,
        sql: str,
        db_path: DbPathType = ":memory:",
        params: Optional[Union[Sequence, dict]] = None,
    ) -> None:
        """类方法快捷执行 SQL"""
        cls._resolve_instance(db_path).execute_query(sql, params=params)

    @classmethod
    def query_df(
        cls,
        sql: str,
        db_path: DbPathType = ":memory:",
        params: Optional[Union[Sequence, dict]] = None,
        temp_views: Optional[dict] = None,
    ) -> pd.DataFrame:
        """类方法快捷查询 DataFrame"""
        return cls._resolve_instance(db_path).query_dataframe(
            sql, params=params, temp_views=temp_views
        )

    @classmethod
    def insert_df(
        cls,
        table_name: str,
        df: pd.DataFrame,
        db_path: DbPathType = ":memory:",
        if_exists: IfExistsMode = "append",
    ) -> None:
        """类方法快捷写入 DataFrame"""
        cls._resolve_instance(db_path).insert_dataframe(table_name, df, if_exists=if_exists)

    @classmethod
    def table_exists(
        cls,
        table_name: str,
        db_path: DbPathType = ":memory:",
    ) -> bool:
        """类方法快捷检查表存在性"""
        return cls._resolve_instance(db_path).has_table(table_name)

    @classmethod
    def get_columns(
        cls,
        table_name: str,
        db_path: DbPathType = ":memory:",
    ) -> List[str]:
        """类方法快捷获取列名列表"""
        return cls._resolve_instance(db_path).get_column_names(table_name)

    @classmethod
    def export_to_parquet(
        cls,
        table_name: str,
        file_path: DbPathType,
        db_path: DbPathType = ":memory:",
    ) -> None:
        """类方法快捷导出 Parquet"""
        cls._resolve_instance(db_path).export_parquet(table_name, file_path)


__all__ = ["DuckDBManager", "DbPathType", "IfExistsMode"]
