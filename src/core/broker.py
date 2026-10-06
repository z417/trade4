from abc import ABC, abstractmethod
from typing import List, Dict, Literal, TypeVar, Generic
import pandas as pd
from .common_dataclasses import WatchlistSecurityModel, SecurityStaticInfoModel

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
    def watchlist_groups(self) -> List[Dict[Literal["id", "name"], int | str]]:
        """所有自选分组"""
        pass

    @property
    def watchlistGroups(self) -> List[Dict[Literal["id", "name"], int | str]]:
        """向后兼容属性别名"""
        return self.watchlist_groups

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

    @abstractmethod
    def get_history_candlesticks(
        self, symbol: str, count: int = 100
    ) -> pd.DataFrame:
        """获取标的历史日K线"""
        pass


__all__ = ["Broker"]

# Test code to verify BrokerA is a singleton
if __name__ == "__main__":

    class BrokerA(Broker):
        def connect(self):
            print("login to broker A")

    # print(BrokerA() == BrokerA())  # Should print: True
