from abc import ABC, abstractmethod


class IMarket(ABC):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(IMarket, cls).__new__(cls, *args, **kw)

    @abstractmethod
    def get_trading_hours(self):
        pass
