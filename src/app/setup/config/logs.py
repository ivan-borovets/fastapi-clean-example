import logging
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, Field

from app.application.common.services.request_id import get_request_id


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
    "[request_id=%(request_id)s] "
    "%(funcName)20s "
    "%(module)s:%(lineno)d "
    "%(levelname)-8s - "
    "%(message)s"
)
DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


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
    logging.getLogger().addFilter(RequestIdFilter())


class LoggingSettings(BaseModel):
    level: LoggingLevel = Field(alias="LEVEL")
