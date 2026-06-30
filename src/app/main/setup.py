import logging

from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.inbound.http.auth_cookie_middleware import AuthCookieMiddleware
from app.inbound.http.errors.internal_server_error import internal_server_error
from app.main.config.logging_ import DATEFMT, FMT, LoggingLevel
from app.main.config.settings import CookieSettings

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


def setup_global_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def handle_unexpected(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=internal_server_error(exc),
        )

    logger.info("Global exception handlers are set up")
