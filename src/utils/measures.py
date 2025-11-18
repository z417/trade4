import asyncio
import os
import sys
import time
from functools import wraps
from typing import Any, AsyncGenerator, Callable


class ProgressBar:
    @staticmethod
    def _clear_line():
        """Clear the current line in the terminal."""
        sys.stdout.write("\033[K")

    @staticmethod
    def _get_terminal_width(default=80) -> int:
        """Get the width of the terminal or use a default value."""
        try:
            _, columns = os.get_terminal_size()
            return columns
        except OSError:
            return default

    @staticmethod
    def _init_bar_percent(
        iteration,
        total,
        decimals,
        fill,
    ):
        bar_length = ProgressBar._get_terminal_width()
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filled_length = int(bar_length * iteration // total)
        bar = fill * filled_length + "-" * (bar_length - filled_length)

        # Clear the line before printing the new progress bar
        ProgressBar._clear_line()
        return bar, percent

    @staticmethod
    def progress_bar_sync(
        iteration,
        total,
        prefix="",
        suffix="",
        decimals=2,
        fill="█",
        refresh_rate=0.1,
    ):
        """
        Update the progress bar synchronously.
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            fill        - Optional  : bar fill character (Str)
            refresh_rate- Optional  : bar refresh rate (float)
        """
        bar, percent = ProgressBar._init_bar_percent(
            iteration,
            total,
            decimals,
            fill,
        )
        # 使用 \r 回车符确保光标回到行首
        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="")
        # Only update the progress bar every `refresh_rate` seconds
        if iteration != 0 and iteration % (total * refresh_rate) == 0:
            sys.stdout.flush()
            time.sleep(refresh_rate)

        if iteration == total:
            print()

    @staticmethod
    async def progress_bar_async(
        iteration,
        total,
        prefix="",
        suffix="",
        decimals=1,
        fill="█",
        refresh_rate=0.1,
    ):
        """
        Update the progress bar asynchronously.
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            fill        - Optional  : bar fill character (Str)
            refresh_rate- Optional  : bar refresh rate (float)
        """
        bar, percent = ProgressBar._init_bar_percent(
            iteration,
            total,
            decimals,
            fill,
        )

        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="")

        # Only update the progress bar every `refresh_rate` seconds
        if iteration != 0 and iteration % (total * refresh_rate) == 0:
            sys.stdout.flush()
            await asyncio.sleep(refresh_rate)

        if iteration == total:
            print()


class TimerDecorator:
    @staticmethod
    def timer(output: Callable, desc: str):
        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwargs):
                start = time.perf_counter()  # 使用 perf_counter 提高精度
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    output(f"{desc}发生异常: {e}")
                    raise e
                else:
                    end = time.perf_counter()
                    output(f"{desc}耗时: {end - start:.2f}秒")
                    return res

            return inner

        return wrapper

    @staticmethod
    def timer_yield(output: Callable, desc: str):
        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwargs):
                start = time.perf_counter()
                generator = func(*args, **kwargs)
                try:
                    yield from generator
                finally:
                    end = time.perf_counter()
                    output(f"{desc}耗时: {end - start:.2f}秒")

            return inner

        return wrapper

    @staticmethod
    def timer_async(output: Callable, desc: str) -> Callable:
        def wrapper(func: Callable[..., Any]) -> Callable:
            @wraps(func)
            async def inner(*args, **kwargs) -> Any:
                start = time.perf_counter()
                try:
                    res = await func(*args, **kwargs)
                except Exception as e:
                    output(f"{desc}发生异常: {e}")
                    raise e
                else:
                    end = time.perf_counter()
                    output(f"{desc}耗时: {end - start:.2f}秒")
                    return res

            return inner

        return wrapper

    @staticmethod
    def timer_async_yield(output: Callable, desc: str) -> Callable:
        def wrapper(func: Callable[..., AsyncGenerator[Any, None]]) -> Callable:
            @wraps(func)
            async def inner(*args, **kwargs) -> AsyncGenerator[Any, None]:
                start = time.perf_counter()
                async_generator = func(*args, **kwargs)
                try:
                    async for item in async_generator:
                        yield item
                finally:
                    end = time.perf_counter()
                    output(f"{desc}耗时: {round((end - start), 2)}秒")

            return inner

        return wrapper


class Timer:
    def __init__(self, out=print, desc="") -> None:
        self.out = out
        self.desc = desc

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.perf_counter()
        self.elapsed_time = self.end_time - self.start_time
        self.out(f"{self.desc}耗时: {self.elapsed_time:.2f}秒")

    @property
    def elapsed(self):
        return self.end_time - self.start_time


class AsyncTimer:
    def __init__(self, out=print, desc=""):
        self.start_time = 0.0
        self.end_time = 0.0
        self.elapsed_time = 0.0
        self.out = out
        self.desc = desc

    async def __aenter__(self):
        self.start_time = asyncio.get_running_loop().time()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.end_time = asyncio.get_running_loop().time()
        self.elapsed_time = self.end_time - self.start_time
        self.out(f"{self.desc}耗时: {self.elapsed_time:.2f}秒")

    @property
    def elapsed(self):
        if self.end_time is None:
            return None
        return self.end_time - self.start_time


if __name__ == "__main__":
    # Synchronous example
    @TimerDecorator.timer(print, "同步函数执行")
    def my():
        for i in range(10):
            ProgressBar.progress_bar_sync(
                i, 10 - 1, prefix="Progress:", suffix="Complete"
            )
            time.sleep(0.1)

    # Asynchronous example
    @TimerDecorator.timer_async(lambda x: print(x), "异步函数执行")
    async def my_async():
        tasks = []
        for _ in range(101):
            task = asyncio.ensure_future(asyncio.sleep(1))
            tasks.append(task)
        for i, task in enumerate(asyncio.as_completed(tasks)):
            await task
            await ProgressBar.progress_bar_async(
                i, 101 - 1, prefix="Async Processing", suffix="Complete"
            )

    @TimerDecorator.timer_yield(lambda x: print(x), "生成器函数执行")
    def generator_function():
        for i in range(5):
            yield i
            time.sleep(0.5)

    my()
    asyncio.run(my_async())

    async def test_AsyncTimer():
        async with AsyncTimer(desc="test_AsyncTimer") as t:
            await asyncio.sleep(1)  # 模拟耗时操作

    asyncio.run(test_AsyncTimer())

    with Timer(desc="test Timer") as t:
        time.sleep(1)  # 模拟耗时操作
