import logging
from io import StringIO

from app.setup.config.logs import configure_logging


def test_configure_logging_debug():
    log_stream = StringIO()

    log = logging.getLogger()
    log.handlers = []

    configure_logging(level="DEBUG")

    for handler in log.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.stream = log_stream

    test_log_msg = "Test log message."
    log.debug(test_log_msg)

    log_output = log_stream.getvalue()
    assert log.level == logging.DEBUG
    assert test_log_msg in log_output
