from abc import ABC, abstractmethod
from typing import List, Dict, Literal, Union
from utils.typevar import TWatchlistSecurity


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

    @abstractmethod
    def get_watchlist(self) -> List[TWatchlistSecurity]:
        """获取所有自选股"""
        pass

    @abstractmethod
    def get_holdings(self):
        """获取当前持仓"""
        pass

    @abstractmethod
    def get_watchlistGroups(self) -> List[Dict[Literal["id", "name"], Union[int, str]]]:
        """获取所有分组"""
        pass


# Test code to verify BrokerA is a singleton
if __name__ == "__main__":

    class BrokerA(IBroker):
        def connect(self):
            print("login to broker A")

    # print(BrokerA() == BrokerA())  # Should print: True
