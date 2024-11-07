# pylint: disable=C0301 (line-too-long)
__all__ = ("initialize_mapping", "create_app_with_container")

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.common.c_infrastructure.persistence.sqla import initialize_mapping
from app.common.d_presentation.http_controllers.exception_handler import (
    ExceptionHandler,
    ExceptionMapper,
    ExceptionMessageProvider,
)
from app.common.d_presentation.http_controllers.router_root import root_router
from app.common.d_presentation.http_middleware.middleware_auth import AuthMiddleware
from app.setup.config.settings import Settings
from app.setup.ioc.ioc_registry import get_providers


def configure_app(new_app: FastAPI) -> None:
    new_app.include_router(root_router)
    new_app.add_middleware(AuthMiddleware)  # noqa
    exception_message_provider: ExceptionMessageProvider = ExceptionMessageProvider()
    exception_mapper: ExceptionMapper = ExceptionMapper()
    exception_handler: ExceptionHandler = ExceptionHandler(
        new_app, exception_message_provider, exception_mapper
    )
    exception_handler.setup_handlers()


def create_app_with_container(settings: Settings) -> FastAPI:
    new_app: FastAPI = FastAPI(default_response_class=ORJSONResponse)
    configure_app(new_app)
    async_container: AsyncContainer = make_async_container(
        *get_providers(), context={Settings: settings}
    )
    setup_dishka(async_container, new_app)
    return new_app
