import pandas as pd
from functools import cached_property
from core import Market
from utils import DuckDBManager


class USMarket(Market):
    """美股市场"""

    def __init__(self, conf):
        super().__init__()
        self.db_path: str = conf.database_path

    def spa_stock_info(self) -> str:
        us_df = Market.fetch_stock_from_sina("US").assign(
            exchange="US",
            symbol=lambda df: df["code"] + ".US",
        )[["symbol", "exchange", "code", "name", "board"]]
        return self._save_securities_to_db(us_df, ("US",))

    @property
    def trading_hours(self):
        """美股交易时间：09:30-16:00 (美东时间)"""
        return {
            "pre_market": ("04:00", "09:30"),
            "regular": ("09:30", "16:00"),
            "post_market": ("16:00", "20:00"),
            "timezone": "America/New_York",
        }

    @cached_property
    def security_list(self):
        return DuckDBManager.query_df(
            sql="SELECT * FROM SECURITY WHERE exchange = ?;",
            db_path=self.db_path,
            params=("US",),
        )
