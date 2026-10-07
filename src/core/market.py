from typing import Callable, Coroutine, NamedTuple, Any
import pandas as pd


class Market(NamedTuple):
    """市场层操作集合 (Immutable Record)"""

    spa_stock_info: Callable[[], Coroutine[Any, Any, str]]
    get_trading_hours: Callable[[], Coroutine[Any, Any, str]]
    get_security_list: Callable[[], Coroutine[Any, Any, pd.DataFrame]]


__all__ = ["Market"]
