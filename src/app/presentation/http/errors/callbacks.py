import logging

log = logging.getLogger(__name__)


def log_info(err: Exception) -> None:
    log.info(f"Handled exception: {type(err).__name__} — {err}")


def log_error(err: Exception) -> None:
    log.error(f"Handled exception: {type(err).__name__} — {err}")
