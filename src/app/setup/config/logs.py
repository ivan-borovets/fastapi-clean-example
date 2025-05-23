import logging
from typing import Final, Literal, cast

LoggingLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

VALID_LOGGING_LEVELS: Final[set[LoggingLevel]] = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def validate_logging_level(*, level: str) -> LoggingLevel:
    if level not in VALID_LOGGING_LEVELS:
        raise ValueError(f"Invalid log level: '{level}'.")
    return cast("LoggingLevel", level)


def configure_logging(*, level: LoggingLevel = "INFO") -> None:
    validate_logging_level(level=level)

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
