import logging
from collections.abc import Iterator

import pytest

from app.setup.config.logs import LoggingLevel, configure_logging


@pytest.fixture
def clean_logging() -> Iterator[None]:
    try:
        yield
    finally:
        logging.getLogger().handlers.clear()


@pytest.mark.parametrize(
    ("lvl_given", "lvl_expected"),
    [
        (LoggingLevel.DEBUG, logging.DEBUG),
        (LoggingLevel.INFO, logging.INFO),
        (LoggingLevel.WARNING, logging.WARNING),
        (LoggingLevel.ERROR, logging.ERROR),
        (LoggingLevel.CRITICAL, logging.CRITICAL),
    ],
)
@pytest.mark.usefixtures("clean_logging")
def test_logger_uses_given_level(
    lvl_given: LoggingLevel,
    lvl_expected: int,
) -> None:
    logger = logging.getLogger()

    configure_logging(level=lvl_given)

    assert logger.level == lvl_expected
