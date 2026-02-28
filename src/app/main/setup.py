import logging

from fastapi import FastAPI

from app.config.logging_ import DATEFMT, FMT, LoggingLevel
from app.config.settings import CookieSettings
from app.presentation.http.auth_cookie_middleware import AuthCookieMiddleware

logger = logging.getLogger(__name__)


def setup_logging(*, level: LoggingLevel = LoggingLevel.INFO) -> None:
    logging.basicConfig(
        level=level,
        datefmt=DATEFMT,
        format=FMT,
        force=True,
    )
    logger.info("Logging is set up")


def setup_middlewares(app: FastAPI, cookie_settings: CookieSettings) -> None:
    app.add_middleware(
        AuthCookieMiddleware,
        cookie_name=cookie_settings.NAME,
        cookie_path=cookie_settings.PATH,
        cookie_httponly=cookie_settings.HTTPONLY,
        cookie_secure=cookie_settings.SECURE,
        cookie_samesite=cookie_settings.SAMESITE,
    )
    logger.info("Middlewares are set up")


def setup_global_exception_handlers(_app: FastAPI) -> None:
    # A place to register global exception handlers
    logger.info("Global exception handlers are set up")
