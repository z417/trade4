from typing import List
from core import Broker, Market


class QuoteService:
    def __init__(self, broker, market):
        self.broker: Broker = broker
        self.market: Market = market

    def test(self):
        # print(self.broker.watchlist)
        # print(self.broker.get_watchlist_by_group("观察"))
        # print(self.broker.watchlistGroups)
        # print(self.broker.holdings)
        # print(self.broker.get_stock_static_info(["06288.HK", "TSLA.US", "002091.SZ"]))
        #
        self.market.spa_stock_info()
        # print(self.market.security_list.query("code=='6288'"))
        pass
