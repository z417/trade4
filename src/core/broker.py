from typing import Callable, Literal, Protocol, NamedTuple, Any, Coroutine
from .common_dataclasses import WatchlistSecurityModel, SecurityStaticInfoModel


import pandas as pd


class GetWatchlistByGroupFunc(Protocol):
    """获取指定组名下的所有标的"""

    def __call__(self, group_name: str) -> Coroutine[Any, Any, list[WatchlistSecurityModel]]: ...


class GetStockStaticInfoFunc(Protocol):
    """获取标的基本信息"""

    def __call__(self, symbols: list[str]) -> Coroutine[Any, Any, list[SecurityStaticInfoModel]]: ...


class GetHistoryCandlesticksFunc(Protocol):
    """获取标的历史日K线（前复权）"""

    def __call__(self, symbol: str, count: int = 100) -> Coroutine[Any, Any, pd.DataFrame]: ...


class Broker(NamedTuple):
    """行情与数据源操作集合"""

    get_watchlist_by_group: GetWatchlistByGroupFunc
    get_watchlist: Callable[[], Coroutine[Any, Any, list[WatchlistSecurityModel]]]  # 所有自选
    get_holdings: Callable[[], Coroutine[Any, Any, list[WatchlistSecurityModel]]]  # 当前持仓
    get_watchlist_groups: Callable[[], Coroutine[Any, Any, list[dict[Literal["id", "name"], int | str]]]]  # 所有分组
    get_stock_static_info: GetStockStaticInfoFunc
    get_account_balance: Callable[[], Coroutine[Any, Any, Any]]  # 资产总览,根据实际返回类型替换 Any
    get_history_candlesticks: GetHistoryCandlesticksFunc  # 历史K线获取


__all__ = ["Broker"]
