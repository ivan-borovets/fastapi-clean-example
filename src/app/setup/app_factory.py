# pylint: disable=C0301 (line-too-long)
__all__ = (
    "create_app",
    "configure_app",
    "create_async_ioc_container",
)

from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse

from app.infrastructure.sqla_persistence.mappings.all import map_tables
from app.presentation.common.asgi_auth_middleware import ASGIAuthMiddleware
from app.presentation.common.exception_handler import ExceptionHandler
from app.setup.config.settings import Settings


def create_app() -> FastAPI:
    return FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    map_tables()
    yield None
    await app.state.dishka_container.close()  # noqa
    # app.state is the place where dishka_container lives


def configure_app(
    app: FastAPI,
    root_router: APIRouter,
) -> None:
    app.include_router(root_router)
    app.add_middleware(ASGIAuthMiddleware)  # noqa
    exception_handler: ExceptionHandler = ExceptionHandler(app)
    exception_handler.setup_handlers()


def create_async_ioc_container(
    providers: Iterable[Provider],
    settings: Settings,
) -> AsyncContainer:
    return make_async_container(
        *providers,
        context={Settings: settings},
    )
