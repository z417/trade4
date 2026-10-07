import asyncio
from typing import Any, AsyncGenerator, Iterable, Coroutine, Callable


async def to_async_iterator(items: Iterable[Any]) -> AsyncGenerator[Any, None]:
    """
    将同步可迭代对象转换为异步迭代器
    """
    for item in items:
        # 这里可以使用 await asyncio.sleep(0) 交出控制权，防止极长列表霸占事件循环
        yield item


def spawn_task(func: Callable[..., Coroutine[Any, Any, Any]], *args: Any) -> asyncio.Task[Any]:
    """
    触发一个异步任务
    """
    return asyncio.create_task(func(*args))


__all__ = ["to_async_iterator", "spawn_task"]
