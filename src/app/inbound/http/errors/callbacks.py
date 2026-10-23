import logging

logger = logging.getLogger(__name__)


def log_info(e: Exception) -> None:
    cause = e.__cause__
    if cause is None:
        logger.info("Handled exception: %s — %s", type(e).__name__, e)
    else:
        logger.info(
            "Handled exception: %s — %s; caused by: %s — %s",
            type(e).__name__,
            e,
            type(cause).__name__,
            cause,
        )
