from typing import List
from core.broker import Broker
from core.market import Market


class QuoteService:
    def __init__(self, broker, market):
        self.broker: Broker = broker
        self.market: Market = market

    def test(self):
        # print(self.broker.get_watchlist())
        # print(self.broker.get_watchlist_by_group("观察"))
        # print(self.broker.get_watchlistGroups())
        # print(self.broker.get_holdings())
        print(self.broker.get_stock_static_info(["700.HK"]))
        pass
