import logging
from unittest.mock import patch

import pytest

from app.setup.config.logs import configure_logging


@pytest.mark.parametrize(
    ("level_str", "expected_level"),
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ],
)
def test_configure_logging_levels(level_str, expected_level):
    with patch("app.setup.config.logs.logging.basicConfig") as mock:
        configure_logging(level=level_str)

        assert mock.call_args[1]["level"] == expected_level
