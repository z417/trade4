from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")


class Market(ABC, Generic[T, R]):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(Market, cls).__new__(cls, *args, **kw)

    @abstractmethod
    def get_trading_hours(self) -> R:
        pass
