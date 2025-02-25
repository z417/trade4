from functools import wraps


def singleton(cls):
    """
    singleton pattern decorator
    :param cls: the object you want to set singleton
    :return:
    """
    _instances = {}

    @wraps(cls)
    def _wrapper(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return _wrapper


__all__ = [
    "singleton",
]
