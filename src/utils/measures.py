import asyncio
import os
import sys
import time
from functools import wraps
from typing import Any, Callable, Coroutine
from contextlib import contextmanager, asynccontextmanager


# ==========================================
# 进度条模块
# ==========================================
def _get_terminal_width(default: int = 80) -> int:
    try:
        _, columns = os.get_terminal_size()
        return columns
    except OSError:
        return default


def _build_bar_string(iteration: int, total: int, decimals: int, fill: str) -> tuple[str, str]:
    bar_length = _get_terminal_width()
    percent_str = f"{100 * (iteration / float(total)):.{decimals}f}"
    filled_length = int(bar_length * iteration // total)
    bar = fill * filled_length + "-" * (bar_length - filled_length)
    return bar, percent_str


async def print_progress_async(
    iteration: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    fill: str = "█",
    refresh_rate: float = 0.1,
) -> None:
    """全异步进度条"""
    bar, percent = _build_bar_string(iteration, total, decimals, fill)
    sys.stdout.write("\033[K")  # Clear line
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="")

    if iteration != 0 and iteration % max(1, int(total * refresh_rate)) == 0:
        sys.stdout.flush()
        await asyncio.sleep(refresh_rate)

    if iteration == total:
        print()


# ==========================================
# 耗时统计模块
# ==========================================
# 1. 函数装饰器
def time_async(desc: str, output: Callable[[str], Any] = print) -> Callable:
    """异步耗时统计装饰器"""

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                output(f"[{desc}] 执行失败: {e}")
                raise
            finally:
                output(f"{desc} 耗时: {time.perf_counter() - start:.2f}秒")

        return wrapper

    return decorator


# 2. 上下文管理器
@contextmanager
def timer_scope(desc: str, output: Callable[[str], Any] = print):
    """同步作用域计时器"""
    start = time.perf_counter()
    try:
        yield  # 将控制权交给 with 语句块
    finally:
        output(f"{desc} 耗时: {time.perf_counter() - start:.2f}秒")


@asynccontextmanager
async def async_timer_scope(desc: str, output: Callable[[str], Any] = print):
    """异步作用域计时器"""
    start = asyncio.get_running_loop().time()
    try:
        yield
    finally:
        output(f"{desc} 耗时: {asyncio.get_running_loop().time() - start:.2f}秒")


__all__ = ["print_progress_async", "time_async", "timer_scope", "async_timer_scope"]

if __name__ == "__main__":
    # Asynchronous example
    @time_async("异步函数执行", print)
    async def my_async():
        tasks = []
        for _ in range(101):
            task = asyncio.ensure_future(asyncio.sleep(1))
            tasks.append(task)
        for i, task in enumerate(asyncio.as_completed(tasks)):
            await task
            await print_progress_async(i, 101 - 1, prefix="Async Processing", suffix="Complete")

    @timer_scope("生成器函数执行", lambda x: print(x))
    def generator_function():
        for i in range(5):
            yield i
            time.sleep(0.5)

    asyncio.run(my_async())

    async def test_async_timer_scope():
        async with async_timer_scope(desc="test async_timer_scope") as t:
            await asyncio.sleep(1)  # 模拟耗时操作

    asyncio.run(test_async_timer_scope())

    with timer_scope(desc="test timer scope") as t:
        time.sleep(1)  # 模拟耗时操作
