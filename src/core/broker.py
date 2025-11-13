from abc import ABC, abstractmethod
from typing import List, Dict, Literal, Union, TypeVar, Generic
from core.data_models import WatchlistSecurityModel

T = TypeVar("T")
R = TypeVar("R")


class Broker(ABC, Generic[T, R]):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(Broker, cls).__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def connect(self, *args: T) -> R:
        """链接到券商平台"""
        pass

    @abstractmethod
    def refresh_watchlist(self) -> List[WatchlistSecurityModel]:
        """刷新自选股"""
        pass

    @abstractmethod
    def get_watchlist_by_group(self, group_name: str) -> List[WatchlistSecurityModel]:
        """获取指定组名下的所有股票"""
        pass

    @abstractmethod
    def get_watchlist(self) -> List[WatchlistSecurityModel]:
        """获取所有自选股"""
        pass

    @abstractmethod
    def get_holdings(self) -> List[WatchlistSecurityModel]:
        """获取当前持仓"""
        pass

    @abstractmethod
    def get_watchlistGroups(self) -> List[Dict[Literal["id", "name"], Union[int, str]]]:
        """获取所有分组"""
        pass

    @abstractmethod
    def get_account_balance(self) -> R:
        """获取资产总览"""
        pass

    @abstractmethod
    def get_stock_static_info(self, symbols: List[str]) -> R:
        pass


# Test code to verify BrokerA is a singleton
if __name__ == "__main__":

    class BrokerA(Broker):
        def connect(self):
            print("login to broker A")

    # print(BrokerA() == BrokerA())  # Should print: True
