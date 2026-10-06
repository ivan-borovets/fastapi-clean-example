import logging

logger = logging.getLogger(__name__)


def log_info(err: Exception) -> None:
    cause = err.__cause__
    if cause is None:
        logger.info("Handled exception: %s — %s", type(err).__name__, err)
    else:
        logger.info(
            "Handled exception: %s — %s; caused by: %s — %s",
            type(err).__name__,
            err,
            type(cause).__name__,
            cause,
        )
