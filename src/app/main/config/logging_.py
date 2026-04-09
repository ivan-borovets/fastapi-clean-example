from enum import StrEnum
from typing import Final

# fmt: off
FMT: Final[str] = (
    "[%(asctime)s.%(msecs)03d] [%(threadName)s] "
    "%(funcName)20s "
    "%(module)s:%(lineno)d "
    "%(levelname)-8s - %(message)s"
)
# fmt: on
DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"


class LoggingLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
