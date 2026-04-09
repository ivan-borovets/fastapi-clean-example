from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from dishka import Provider, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.infrastructure.persistence_sqla.mappings.all import map_tables
from app.main.config.loader import (
    load_app_settings,
    load_cookie_settings,
    load_jwt_settings,
    load_password_hasher_settings,
    load_postgres_settings,
    load_session_settings,
    load_sqla_settings,
)
from app.main.config.settings import (
    AppSettings,
    CookieSettings,
    JwtSettings,
    PasswordHasherSettings,
    PostgresSettings,
    SessionSettings,
    SqlaSettings,
)
from app.main.ioc.provider_registry import get_providers
from app.main.setup import setup_global_exception_handlers, setup_logging, setup_middlewares
from app.presentation.http.root_router import make_fastapi_root_router


def make_lifespan() -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Here one can bind APP-scoped dependencies to `app.state` and close them if needed"""
        # https://dishka.readthedocs.io/en/stable/integrations/fastapi.html
        container = app.state.dishka_container
        try:
            map_tables()
            yield
        finally:
            await container.close()

    return lifespan


def make_app(
    *di_providers: Provider,
    app_settings: AppSettings | None = None,
    postgres_settings: PostgresSettings | None = None,
    sqla_settings: SqlaSettings | None = None,
    password_hasher_settings: PasswordHasherSettings | None = None,
    jwt_settings: JwtSettings | None = None,
    session_settings: SessionSettings | None = None,
    cookie_settings: CookieSettings | None = None,
) -> FastAPI:
    """Pass providers to override existing ones for testing."""
    if app_settings is None:
        app_settings = load_app_settings()

    setup_logging(level=app_settings.LOGGING_LEVEL)

    if postgres_settings is None:
        postgres_settings = load_postgres_settings()
    if sqla_settings is None:
        sqla_settings = load_sqla_settings()
    if password_hasher_settings is None:
        password_hasher_settings = load_password_hasher_settings()
    if jwt_settings is None:
        jwt_settings = load_jwt_settings()
    if session_settings is None:
        session_settings = load_session_settings()
    if cookie_settings is None:
        cookie_settings = load_cookie_settings()

    app = FastAPI(
        debug=app_settings.DEBUG_MODE,
        title=app_settings.SERVICE_NAME,
        version=app_settings.VERSION,
        summary=f"OpenAPI schema for {app_settings.SERVICE_NAME}",
        lifespan=make_lifespan(),
        root_path=app_settings.ROOT_PATH.rstrip("/"),
    )
    container = make_async_container(
        *get_providers(),
        *di_providers,
        context={
            AppSettings: app_settings,
            PostgresSettings: postgres_settings,
            SqlaSettings: sqla_settings,
            PasswordHasherSettings: password_hasher_settings,
            JwtSettings: jwt_settings,
            SessionSettings: session_settings,
            CookieSettings: cookie_settings,
        },
    )
    setup_dishka(container, app)
    setup_middlewares(app, cookie_settings)
    setup_global_exception_handlers(app)
    app.include_router(
        make_fastapi_root_router(
            debug_mode=app_settings.DEBUG_MODE,
            cookie_name=cookie_settings.NAME,
        )
    )
    return app


if __name__ == "__main__":
    """See clck.ru/3RUG2j if debug in PyCharm is broken"""
    import uvicorn

    uvicorn.run(app=make_app())
