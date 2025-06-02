__all__ = (
    "configure_app",
    "create_app",
    "create_async_ioc_container",
)

from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse

from app.infrastructure.sqla_persistence.mappings.all import map_tables
from app.presentation.web.asgi_auth_middleware import (
    ASGIAuthMiddleware,
)
from app.presentation.web.exception_handlers import ExceptionHandler
from app.setup.config.settings import AppSettings


def create_app() -> FastAPI:
    return FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    map_tables()
    yield None
    await app.state.dishka_container.close()
    # https://dishka.readthedocs.io/en/stable/integrations/fastapi.html


def configure_app(
    app: FastAPI,
    root_router: APIRouter,
) -> None:
    app.include_router(root_router)
    app.add_middleware(ASGIAuthMiddleware)
    # https://github.com/encode/starlette/discussions/2451
    exception_handler = ExceptionHandler(app)
    exception_handler.setup_handlers()


def create_async_ioc_container(
    providers: Iterable[Provider],
    settings: AppSettings,
) -> AsyncContainer:
    return make_async_container(
        *providers,
        context={AppSettings: settings},
    )
