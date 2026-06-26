"""日志记录功能。

对应 PRD 4.4.3：记录系统运行过程中的所有事件与错误。

日志级别：DEBUG、INFO、WARNING、ERROR。
日志内容：时间戳、日志级别、模块名称、消息内容。
业务逻辑：
    1. 日志同时输出到控制台与文件。
    2. 日志文件按周期切割，保留历史日志。（TODO：可用 TimedRotatingFileHandler）
    3. 错误日志可单独记录。（TODO）
"""

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str, log_file: str = "gui_agent.log") -> logging.Logger:
    """获取一个同时输出到控制台和文件的 logger。

    Args:
        name: logger 名称，通常传模块名（如 "perception.screenshot"）。
        log_file: 日志文件路径。

    Returns:
        配置好的 logging.Logger 实例。
    """
    logger = logging.getLogger(name)
    if logger.handlers:  # 避免重复添加 handler
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(_LOG_FORMAT)

    # 控制台输出
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # 文件输出
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
