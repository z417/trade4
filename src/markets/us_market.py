import pandas as pd
from typing import Dict
from functools import cached_property
from core import Market
from utils import DuckDBManager


class USMarket(Market):
    """美股市场"""

    def __init__(self, conf: Dict):
        super().__init__()
        self.db_path: str = conf.get("DB_PATH", ":memory:")

    def spa_stock_info(self) -> str:
        table_name = "SECURITY"
        if DuckDBManager.table_exists(table_name, self.db_path):
            DuckDBManager.execute(
                f"DELETE FROM {table_name} WHERE EXCHANGE = ?;",
                self.db_path,
                params=("US",),
            )
        DuckDBManager.insert_df(
            table_name,
            Market.fetch_stock_from_eastmoney("US").assign(exchange="US"),
            self.db_path,
        )
        return table_name

    @property
    def trading_hours(self):
        print("USMarket: Getting trading hours...")

    @cached_property
    def security_list(self):
        return DuckDBManager.query_df(
            sql="SELECT * FROM security WHERE EXCHANGE = ?;",
            db_path=self.db_path,
            params=("US",),
        )
