import asyncio
import functools
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable, Optional
from .duckdb_manager import DuckDBManager
from .measures import AsyncTimer, ProgressBar, Timer, TimerDecorator


class AsyncIteratorFactory:
    """异步列表迭代器"""

    def __init__(self, items: Iterable) -> None:
        self.items = items

    def __aiter__(self) -> "AsyncIteratorFactory":
        return self

    async def __anext__(self) -> Any:
        try:
            item = next(self.items_iter)
        except StopIteration:
            # 明确地抛出StopAsyncIteration异常,并与原始异常分开
            raise StopAsyncIteration from None
        return item

    async def iterate(self) -> AsyncIterator[Any]:
        self.items_iter = iter(self.items)
        async for item in self:
            yield item


def create_task(
    func: Callable[..., Awaitable],
    *args: Any,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> asyncio.Task:
    """
    创建一个任务, 用于异步执行给定的函数。
    :param func: 要异步执行的函数。
    :param args: 传递给函数的参数。
    :param loop: 可选的事件循环。
    :return: 一个 Task 对象, 代表正在执行的异步操作。
    """
    return asyncio.ensure_future(functools.partial(func, *args)(), loop=loop)


__all__ = [
    "TimerDecorator",
    "ProgressBar",
    "DuckDBManager",
    "Timer",
    "AsyncTimer",
    "AsyncIteratorFactory",
]
