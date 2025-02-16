from typing import List
from utils.typevar import TWatchlistSecurity
from brokers.IBroker import IBroker


class QuoteService:
    def __init__(self, broker, market):
        self.broker: IBroker = broker
        self.market = market
        self.broker.connect()

    def get_watchlist(self) -> List[TWatchlistSecurity]:
        """获取所有自选股"""
        return self.broker.get_watchlist()
