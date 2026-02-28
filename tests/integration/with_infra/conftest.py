import os
from collections.abc import AsyncIterator, Sequence
from typing import Final, cast

import asgi_lifespan
import httpx
import pytest
from dishka import Provider
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config.settings import AppSettings
from app.infrastructure.persistence_sqla.registry import mapper_registry
from app.main.run import make_app

LIFESPAN_MANAGER_STARTUP_TIMEOUT_S: Final[int] = 30
ALLOW_DESTRUCTIVE_TEST_CLEANUP: Final[str] = "ALLOW_DESTRUCTIVE_TEST_CLEANUP"
ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE: Final[str] = "1"


@pytest.fixture(scope="session")
def allow_destructive() -> None:
    """Use on fixtures that require potentially dangerous cleanup."""
    if os.getenv(ALLOW_DESTRUCTIVE_TEST_CLEANUP) != ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE:
        raise pytest.UsageError(
            "Destructive cleanup is disabled: "
            f"{ALLOW_DESTRUCTIVE_TEST_CLEANUP} must be set to {ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE}. "
            "This guard prevents accidental cleanup of non-test data."
        )


@pytest.fixture
def it_di_overrides() -> Sequence[Provider]:
    """
    Override in a test module to provide custom dependency overrides.
    Keep the same fixture signature.
    """
    return ()


@pytest.fixture
def it_fastapi_app(it_di_overrides: Sequence[Provider]) -> FastAPI:
    return make_app(
        *it_di_overrides,
        app_settings=AppSettings(DEBUG_MODE=False),
    )


@pytest.fixture
async def it_client(it_fastapi_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with (
        asgi_lifespan.LifespanManager(
            it_fastapi_app,
            startup_timeout=LIFESPAN_MANAGER_STARTUP_TIMEOUT_S,
        ),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=it_fastapi_app),
            base_url="http://test",
        ) as client,
    ):
        yield client


@pytest.fixture
async def it_sessionmaker(
    it_client: httpx.AsyncClient,
    it_fastapi_app: FastAPI,
) -> async_sessionmaker[AsyncSession]:
    container = it_fastapi_app.state.dishka_container
    session_maker = await container.get(async_sessionmaker[AsyncSession])
    return cast(async_sessionmaker[AsyncSession], session_maker)


@pytest.fixture
async def it_db_clean(
    allow_destructive: None,
    it_sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    table_names = [table.name for table in mapper_registry.metadata.sorted_tables if table.name != "alembic_version"]
    assert table_names, "it_db_clean: no tables found in mapper_registry.metadata (fixture is a no-op)"
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
