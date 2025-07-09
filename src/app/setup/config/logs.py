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


class LoggingSettings(BaseModel):
    level: LoggingLevel = Field(alias="LEVEL")


DEFAULT_LOG_LEVEL: Final[LoggingLevel] = LoggingLevel.INFO


def configure_logging(*, level: LoggingLevel = DEFAULT_LOG_LEVEL) -> None:
    logging.getLogger().handlers.clear()

    logging.basicConfig(
        level=getattr(logging, level),
        datefmt="%Y-%m-%d %H:%M:%S",
        format=(
            "[%(asctime)s.%(msecs)03d] "
            "%(funcName)20s "
            "%(module)s:%(lineno)d "
            "%(levelname)-8s - "
            "%(message)s"
        ),
    )
