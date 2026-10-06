import os
import subprocess
import sys
from collections.abc import AsyncIterator, Sequence
from typing import Final

import asgi_lifespan
import httpx2
import pytest
from dishka import AsyncContainer, Provider
from fastapi import APIRouter, FastAPI
from sqlalchemy import Engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.inbound.http.root_router import make_fastapi_root_router
from app.main.config.loader import BASE_DIR, load_cookie_settings, load_session_settings, load_sqla_settings
from app.main.config.settings import AppSettings, CookieSettings, PostgresSettings, SessionSettings, SqlaSettings
from app.main.run import make_app
from app.outbound.persistence_sqla.engine import make_async_engine, make_async_sessionmaker
from app.outbound.persistence_sqla.mappings.all import map_tables
from app.outbound.persistence_sqla.registry import mapper_registry
from tests.integration.with_infra.authentication import authenticate
from tests.integration.with_infra.factories import create_raw_password, create_user_with_password

LIFESPAN_MANAGER_STARTUP_TIMEOUT_S: Final[int] = 30


@pytest.fixture(scope="session")
def it_mapped_tables() -> None:
    map_tables()


@pytest.fixture(scope="session")
def it_sqla_settings() -> SqlaSettings:
    return load_sqla_settings()


@pytest.fixture(scope="session")
def it_auth_session_settings() -> SessionSettings:
    return load_session_settings()


@pytest.fixture(scope="session")
def it_cookie_settings() -> CookieSettings:
    return load_cookie_settings()


@pytest.fixture(scope="session")
def it_worker_postgres_settings(
    allow_destructive: None,
    it_postgres_settings: PostgresSettings,
    it_maintenance_db_engine: Engine,
    it_template_postgres_settings: PostgresSettings,
    worker_id: str,
) -> PostgresSettings:
    """
    Own migrated database per worker; `worker_id` is `master` when pytest runs without `-n`.
    Alembic runs in a subprocess: `env.py` reconfigures global logging.
    """
    settings = PostgresSettings(
        DB=f"{it_postgres_settings.DB}_{worker_id}",
        HOST=it_postgres_settings.HOST,
        PORT=it_postgres_settings.PORT,
        USER=it_postgres_settings.USER,
        PASSWORD=it_postgres_settings.PASSWORD,
    )

    with it_maintenance_db_engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{settings.DB}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{settings.DB}" TEMPLATE "{it_template_postgres_settings.DB}"'))

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BASE_DIR,
        env=os.environ | {"POSTGRES_DB": settings.DB},
        check=True,
    )

    return settings


@pytest.fixture
async def it_engine(
    it_worker_postgres_settings: PostgresSettings,
    it_sqla_settings: SqlaSettings,
) -> AsyncIterator[AsyncEngine]:
    engine = make_async_engine(
        dsn=it_worker_postgres_settings.dsn,
        echo=it_sqla_settings.ECHO,
        echo_pool=it_sqla_settings.ECHO_POOL,
        pool_size=it_sqla_settings.POOL_SIZE,
        max_overflow=it_sqla_settings.MAX_OVERFLOW,
        connect_timeout_s=it_sqla_settings.CONNECT_TIMEOUT_S,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
def it_sessionmaker(
    it_mapped_tables: None,
    it_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return make_async_sessionmaker(it_engine)


@pytest.fixture
async def it_db_clean(
    allow_destructive: None,
    it_mapped_tables: None,
    it_sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    table_names = [table.name for table in mapper_registry.metadata.sorted_tables if table.name != "alembic_version"]
    if not table_names:
        return

    sql = "TRUNCATE " + ", ".join(f'"{name}"' for name in table_names) + " RESTART IDENTITY CASCADE;"

    async with it_sessionmaker() as session:
        await session.execute(text(sql))
        await session.commit()


@pytest.fixture
async def it_session(
    it_db_clean: None,
    it_sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with it_sessionmaker() as session:
        yield session


@pytest.fixture
def it_di_overrides() -> Sequence[Provider]:
    """
    Override in a test module to provide custom dependency overrides.
    Keep the same fixture signature.
    """
    return ()


@pytest.fixture(scope="session")
def it_http_root_router(it_cookie_settings: CookieSettings) -> APIRouter:
    return make_fastapi_root_router(debug=False, cookie_name=it_cookie_settings.NAME)


@pytest.fixture
def it_fastapi_app(
    it_di_overrides: Sequence[Provider],
    it_worker_postgres_settings: PostgresSettings,
    it_sqla_settings: SqlaSettings,
    it_auth_session_settings: SessionSettings,
    it_cookie_settings: CookieSettings,
    it_http_root_router: APIRouter,
) -> FastAPI:
    return make_app(
        *it_di_overrides,
        app_settings=AppSettings(DEBUG_MODE=False),
        postgres_settings=it_worker_postgres_settings,
        sqla_settings=it_sqla_settings,
        session_settings=it_auth_session_settings,
        cookie_settings=it_cookie_settings,
        fastapi_root_router=it_http_root_router,
    )


@pytest.fixture
async def it_app_container(it_fastapi_app: FastAPI) -> AsyncIterator[AsyncContainer]:
    """Owns the container for tests that skip `it_client` and its lifespan."""
    container: AsyncContainer = it_fastapi_app.state.dishka_container
    try:
        yield container
    finally:
        await container.close()


@pytest.fixture
async def it_client(
    it_db_clean: None,
    it_fastapi_app: FastAPI,
) -> AsyncIterator[httpx2.AsyncClient]:
    async with (
        asgi_lifespan.LifespanManager(
            it_fastapi_app,
            startup_timeout=LIFESPAN_MANAGER_STARTUP_TIMEOUT_S,
        ),
        httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=it_fastapi_app),
            base_url="http://test",
        ) as client,
    ):
        yield client


@pytest.fixture
async def it_user_service(
    it_client: httpx2.AsyncClient,
    it_fastapi_app: FastAPI,
) -> UserService:
    container: AsyncContainer = it_fastapi_app.state.dishka_container
    return await container.get(UserService)


@pytest.fixture
def it_authenticated_user_password() -> str:
    return create_raw_password()


@pytest.fixture
async def it_authenticated_user(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
    it_authenticated_user_password: str,
) -> User:
    user = await create_user_with_password(it_user_service, raw_password=it_authenticated_user_password)
    it_session.add(user)
    await it_session.commit()
    await authenticate(it_client, username=user.username.value, password=it_authenticated_user_password)
    return user
