from abc import ABC, abstractmethod


class IAi(ABC):
    _instances = {}

    def __new__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(IAi, cls).__new__(cls, *args, **kw)
        return cls._instances[cls]

    @abstractmethod
    def login(self):
        """登ai平台"""
        pass
