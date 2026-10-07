import sys
from loguru import logger


def setup_logger(log_level: str = "INFO", log_file: str | None = "logs/app.log") -> None:
    """初始化全局异步日志系统"""
    logger.remove()

    stdout_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(sys.stdout, format=stdout_format, level=log_level, colorize=True)

    if log_file:
        logger.add(
            log_file,
            rotation="00:00",
            retention="7 days",
            compression="zip",
            level=log_level,
            enqueue=True,  # 开启异步队列，绝不阻塞 asyncio 事件循环
        )


__all__ = ["logger", "setup_logger"]
