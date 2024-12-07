# pylint: disable=C0301 (line-too-long)
__all__ = ("initialize_mapping", "create_app_with_container")

from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.infrastructure.persistence.sqla import initialize_mapping
from app.presentation.exception_handler import (
    ExceptionHandler,
    ExceptionMapper,
    ExceptionMessageProvider,
)
from app.presentation.http_routers.router_root import root_router
from app.presentation.middleware_auth import AuthMiddleware
from app.setup.config.settings import Settings
from app.setup.ioc.ioc_registry import get_providers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield None
    await app.state.dishka_container.close()  # noqa; app.state is the place where dishka_container lives


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
    new_app: FastAPI = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
    configure_app(new_app)
    async_container: AsyncContainer = make_async_container(
        *get_providers(), context={Settings: settings}
    )
    setup_dishka(async_container, new_app)
    return new_app
