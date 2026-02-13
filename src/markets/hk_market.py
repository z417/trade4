import pandas as pd
from functools import cached_property
from requests import Session
from io import BytesIO
from core import Market
from utils import DuckDBManager


class HKMarket(Market):
    """港股市场"""

    def __init__(self, conf):
        super().__init__()
        self.db_path: str = conf.database_path

    def _spa_stock_info_from_hkex(self) -> pd.DataFrame:
        with Session() as s:
            tmp_df = (
                pd.read_excel(
                    BytesIO(
                        s.get(
                            "https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/services/trading/securities/securitieslists/ListOfSecurities_c.xlsx",
                            timeout=15,
                        ).content
                    ),
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
                )[["exchange", "code", "name", "board"]]
            )
        return tmp_df

    def spa_stock_info(self) -> str:
        table_name = "SECURITY"
        if DuckDBManager.table_exists(table_name, self.db_path):
            DuckDBManager.execute(
                f"DELETE FROM {table_name} WHERE EXCHANGE = ?;",
                self.db_path,
                params=("HK",),
            )
        DuckDBManager.insert_df(
            table_name,
            self._spa_stock_info_from_hkex(),
            # Market.fetch_stock_from_eastmoney("HKEX").assign(exchange="HK"),
            self.db_path,
        )
        return table_name

    @property
    def trading_hours(self):
        print("HKMarket: Getting trading hours...")

    @cached_property
    def security_list(self):
        return DuckDBManager.query_df(
            sql="SELECT * FROM security WHERE EXCHANGE = ?;",
            db_path=self.db_path,
            params=("HK",),
        )
