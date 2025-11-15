from abc import ABC, abstractmethod
from typing import List, Dict, Literal, Union, TypeVar, Generic
from core.data_models import WatchlistSecurityModel, SecurityStaticInfoModel

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
    def get_watchlist_by_group(self, group_name: str) -> List[WatchlistSecurityModel]:
        """获取指定组名下的所有标的"""
        pass

    @property
    @abstractmethod
    def watchlist(self) -> List[WatchlistSecurityModel]:
        """所有自选"""
        pass

    @property
    @abstractmethod
    def holdings(self) -> List[WatchlistSecurityModel]:
        """当前持仓"""
        pass

    @property
    @abstractmethod
    def watchlistGroups(self) -> List[Dict[Literal["id", "name"], int | str]]:
        """所有分组"""
        pass

    @property
    @abstractmethod
    def account_balance(self) -> R:
        """资产总览
        TODO: 放在这里是否合适？交易和数据获取可以分开
        """
        pass

    @abstractmethod
    def get_stock_static_info(
        self, symbols: List[str]
    ) -> List[SecurityStaticInfoModel]:
        """获取标的基本信息"""
        pass


# Test code to verify BrokerA is a singleton
if __name__ == "__main__":

    class BrokerA(Broker):
        def connect(self):
            print("login to broker A")

    # print(BrokerA() == BrokerA())  # Should print: True
