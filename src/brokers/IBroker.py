from abc import ABC, abstractmethod
from typing import List, Dict, Literal, Union
from utils.typevar import *


class IBroker(ABC):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(IBroker, cls).__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def connect(self):
        """链接到券商平台"""
        pass

    @abstractmethod
    def refresh_watchlist(self) -> List[TWatchlistSecurity]:
        """刷新自选股"""
        pass

    @abstractmethod
    def get_watchlist_by_group(self, group_name: str) -> List[TWatchlistSecurity]:
        """获取指定组名下的所有股票"""
        pass

    @property
    @abstractmethod
    def allWatchlist(self) -> List[TWatchlistSecurity]:
        """获取所有自选股"""
        pass

    @property
    @abstractmethod
    def holdings(self) -> List[TWatchlistSecurity]:
        """获取当前持仓"""
        pass

    @property
    @abstractmethod
    def watchlistGroups(self) -> List[Dict[Literal["id", "name"], Union[int, str]]]:
        """获取所有分组"""
        pass

    @abstractmethod
    def pull_static_info(self, symbols: List[str]) -> List[TSecurityStaticInfo]:
        """获取标的基础信息"""
        pass

    @abstractmethod
    def pull_quote(self, symbols: List[str]) -> List[TSecurityQuote]:
        """获取标的实时行情"""
        pass

    @abstractmethod
    def pull_depth(self, symbol: str) -> Dict[Literal["bids", "asks"], List[TDepth]]:
        """获取标的盘口"""
        pass

    @abstractmethod
    def pull_intraday(self, symbol: str) -> List[TIntradayLine]:
        """获取标的分时"""
        pass


# Test code to verify BrokerA is a singleton
if __name__ == "__main__":

    class BrokerA(IBroker):
        def connect(self):
            print("login to broker A")

    # print(BrokerA() == BrokerA())  # Should print: True
