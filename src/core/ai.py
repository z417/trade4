from typing import Callable, Coroutine, NamedTuple, Any


class AiService(NamedTuple):
    """AI 服务集合 (Immutable Record)"""

    analyze: Callable[[str], Coroutine[Any, Any, str]]


__all__ = ["AiService"]
