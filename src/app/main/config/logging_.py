from typing import Final, Literal

# fmt: off
FMT: Final[str] = (
    "[%(asctime)s.%(msecs)03d] [%(threadName)s] "
    "%(funcName)20s "
    "%(module)s:%(lineno)d "
    "%(levelname)-8s - %(message)s"
)
# fmt: on
DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
