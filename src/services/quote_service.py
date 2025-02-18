from typing import List, Literal, Union, Dict
from utils.typevar import *
from brokers.IBroker import IBroker


class QuoteService:
    def __init__(self, broker, market):
        self.broker: IBroker = broker
        self.market = market
        self.broker.connect()

    @property
    def allWatchlist(self) -> List[TWatchlistSecurity]:
        """获取所有自选股"""
        return self.broker.allWatchlist

    @property
    def watchlistGroups(self) -> List[Dict[Literal["id", "name"], Union[int, str]]]:
        """获取所有分组"""
        return self.broker.watchlistGroups

    @property
    def holdings(self) -> List[TWatchlistSecurity]:
        """获取所有自选股"""
        return self.broker.holdings

    def get_watchlist_by_group(self, group_name: str) -> List[TWatchlistSecurity]:
        """获取指定组名下的所有股票"""
        return self.broker.get_watchlist_by_group(group_name)

    def pull_static_info(self, symbols: List[str]) -> List[TSecurityStaticInfo]:
        """获取标的基础信息"""
        return self.broker.pull_static_info(symbols)

    def pull_quote(self, symbols: List[str]) -> List[TSecurityQuote]:
        """获取标的行情"""
        return self.broker.pull_quote(symbols)

    def pull_depth(self, symbol: str) -> Dict[Literal["bids", "asks"], List[TDepth]]:
        """获取标的深度"""
        return self.broker.pull_depth(symbol)

    def pull_intraday(self, symbol: str) -> List[TIntradayLine]:
        """获取标的分时"""
        return self.broker.pull_intraday(symbol)
