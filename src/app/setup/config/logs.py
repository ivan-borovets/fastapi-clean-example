import logging
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, Field


class LoggingLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


DEFAULT_LOG_LEVEL: Final[LoggingLevel] = LoggingLevel.INFO

FMT: Final[str] = (
    "[%(asctime)s.%(msecs)03d] "
    "[%(threadName)s] "
    "%(funcName)20s "
    "%(module)s:%(lineno)d "
    "%(levelname)-8s - "
    "%(message)s"
)
DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    *,
    level: LoggingLevel = DEFAULT_LOG_LEVEL,
) -> None:
    logging.basicConfig(
        level=level,
        datefmt=DATEFMT,
        format=FMT,
        force=True,
    )


class LoggingSettings(BaseModel):
    level: LoggingLevel = Field(alias="LEVEL")
