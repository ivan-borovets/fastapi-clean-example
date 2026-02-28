import logging

logger = logging.getLogger(__name__)


def log_info(err: Exception) -> None:
    logger.info("Handled exception: %s — %s", type(err).__name__, err)
