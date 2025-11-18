import pandas as pd
from typing import Dict
from functools import cached_property
from core import Market
from utils import DuckDBManager


class CNMarket(Market):
    """A股市场"""

    def __init__(self, conf: Dict):
        super().__init__()
        self.db_path: str = conf.get("DB_PATH", ":memory:")

    def spa_stock_info(self) -> str:
        table_name = "SECURITY"
        stock_sz = Market.fetch_stock_from_eastmoney(
            "SZSE",
        ).assign(
            exchange="SZ",
            code=lambda df: df["code"]
            .astype(str)
            .str.split(".", expand=True)
            .iloc[:, 0]
            .str.zfill(6)
            .str.replace("000nan", ""),
        )
        stock_sh = Market.fetch_stock_from_eastmoney("SSE").assign(exchange="SH")
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
