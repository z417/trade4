from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

T = TypeVar("T")
R = TypeVar("R")


class BaseAi(ABC, Generic[T, R]):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(BaseAi, cls).__new__(cls, *args, **kw)
        return cls._instances[cls]

    @abstractmethod
    def login(self, *args: T, **kw: Any) -> R:
        """登ai平台"""
        pass
