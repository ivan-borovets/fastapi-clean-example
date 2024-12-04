import logging
from typing import Literal

LoggingLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def configure_logging(level: LoggingLevel = "INFO") -> None:
    level_map: dict[LoggingLevel, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    numeric_level: int = level_map.get(level, logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=(
            "[%(asctime)s.%(msecs)03d] "
            "%(funcName)20s "
            "%(module)s:%(lineno)d "
            "%(levelname)-8s - "
            "%(message)s"
        ),
    )
