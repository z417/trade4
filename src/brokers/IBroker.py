from abc import ABC, abstractmethod
from typing import List, Dict, Literal, TypeVar, Generic, Any
from utils.typevar import *

T = TypeVar("T", contravariant=True)
# R = TypeVar("R", covariant=True)


class IBroker(ABC, Generic[T]):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(IBroker, cls).__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def connect(self, *args: T, **kw: Any) -> None:
        """链接到券商平台"""
        pass

    @abstractmethod
    def refresh_watchlist(self, *args: T, **kw: Any) -> None:
        """刷新自选股"""
        pass

    @abstractmethod
    def get_watchlist_by_group(self, *args: T, **kw: Any) -> List[TWatchlistSecurity]:
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
    def watchlistGroups(self) -> List[Dict[Literal["id", "name"], int | str]]:
        """获取所有分组"""
        pass

    @abstractmethod
    def pull_static_info(self, *args: T, **kw: Any) -> List[TSecurityStaticInfo]:
        """获取标的基础信息"""
        pass

    @abstractmethod
    def pull_quote(self, *args: T, **kw: Any) -> List[TSecurityQuote]:
        """获取标的实时行情"""
        pass

    @abstractmethod
    def pull_depth(
        self, *args: T, **kw: Any
    ) -> Dict[Literal["bids", "asks"], List[TDepth]]:
        """获取标的盘口"""
        pass

    @abstractmethod
    def pull_intraday(self, *args: T, **kw: Any) -> List[TIntradayLine]:
        """获取标的分时"""
        pass

    @abstractmethod
    def pull_history_candlesticks_by_offset(
        self, *args: T, **kw: Any
    ) -> List[TCandlesticks]:
        """按时间偏移获取标的历史K线"""
        pass

    @abstractmethod
    def pull_history_candlesticks_by_date(
        self, *args: T, **kw: Any
    ) -> List[TCandlesticks]:
        """按日期获取标的历史K线"""
        pass

    @abstractmethod
    def pull_capital_flow(
        self, *args: T, **kw: Any
    ) -> List[Dict[Literal["inflow", "timestamp"], Decimal | datetime]]:
        """获取标的当日的资金流向(每分钟)"""
        pass

    @abstractmethod
    def pull_capital_distribution(self, *args: T, **kw: Any) -> Dict[
        Literal[
            "timestamp",
            "capital_in",
            "capital_out",
        ],
        datetime
        | Dict[
            Literal[
                "large",
                "medium",
                "small",
            ],
            Decimal,
        ],
    ]:
        """获取标的当日的资金分布"""
        pass

    @abstractmethod
    def pull_calc_indexes(self, *args: T, **kw: Any):
        """获取标的计算指标"""
        pass

    @abstractmethod
    def pull_candlesticks(self, *args: T, **kw: Any):
        """获取标的 K 线"""


# Test code to verify BrokerA is a singleton
if __name__ == "__main__":

    class BrokerA(IBroker):
        def connect(self):
            print("login to broker A")

    # print(BrokerA() == BrokerA())  # Should print: True
