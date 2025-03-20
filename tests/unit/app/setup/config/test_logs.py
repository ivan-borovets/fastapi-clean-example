import logging
from unittest.mock import MagicMock

import pytest

from app.setup.config.logs import configure_logging, validate_logging_level


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_validate_logging_level_valid(level):
    assert validate_logging_level(level=level) == level


@pytest.mark.parametrize("level", ["", "debug", "INVALID_LEVEL", "INFOO"])
def test_validate_logging_level_invalid(level):
    with pytest.raises(ValueError):
        validate_logging_level(level=level)


@pytest.mark.parametrize(
    "level_str, expected_level",
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ],
)
def test_configure_logging_levels(level_str, expected_level, monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(logging, "basicConfig", mock)
    configure_logging(level=level_str)
    assert mock.call_args[1]["level"] == expected_level
