import logging
from enum import StrEnum
from typing import Final


class LoggingLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


DEFAULT_LOG_LEVEL: Final[LoggingLevel] = LoggingLevel.INFO


def configure_logging(*, level: LoggingLevel = DEFAULT_LOG_LEVEL) -> None:
    logging.getLogger().handlers.clear()

    level_map: dict[LoggingLevel, int] = {
        LoggingLevel.DEBUG: logging.DEBUG,
        LoggingLevel.INFO: logging.INFO,
        LoggingLevel.WARNING: logging.WARNING,
        LoggingLevel.ERROR: logging.ERROR,
        LoggingLevel.CRITICAL: logging.CRITICAL,
    }

    logging.basicConfig(
        level=level_map[level],
        datefmt="%Y-%m-%d %H:%M:%S",
        format=(
            "[%(asctime)s.%(msecs)03d] "
            "%(funcName)20s "
            "%(module)s:%(lineno)d "
            "%(levelname)-8s - "
            "%(message)s"
        ),
    )
