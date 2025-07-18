import logging
from collections.abc import AsyncIterator
from typing import cast

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.adapters.types import (
    MainAsyncSession,
)
from app.infrastructure.auth.adapters.types import AuthAsyncSession
from app.infrastructure.persistence_sqla.config import PostgresDsn, SqlaEngineConfig

log = logging.getLogger(__name__)


async def get_async_engine(
    dsn: PostgresDsn,
    engine_config: SqlaEngineConfig,
) -> AsyncIterator[AsyncEngine]:
    async_engine = create_async_engine(
        url=dsn,
        echo=engine_config.echo,
        echo_pool=engine_config.echo_pool,
        pool_size=engine_config.pool_size,
        max_overflow=engine_config.max_overflow,
        connect_args={"connect_timeout": 5},
        pool_pre_ping=True,
    )
    log.debug("Async engine created with DSN: %s", dsn)
    yield async_engine
    log.debug("Disposing async engine...")
    await async_engine.dispose()
    log.debug("Engine is disposed.")


def get_async_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
    log.debug("Async session maker initialized.")
    return async_session_factory


async def get_main_async_session(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[MainAsyncSession]:
    log.debug("Starting Main async session...")
    async with async_session_factory() as session:
        log.debug("Main async session started.")
        yield cast(MainAsyncSession, session)
        log.debug("Closing async session.")
    log.debug("Main async session closed.")


async def get_auth_async_session(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AuthAsyncSession]:
    log.debug("Starting Auth async session...")
    async with async_session_factory() as session:
        log.debug("Async session started for Auth.")
        yield cast(AuthAsyncSession, session)
        log.debug("Closing async session.")
    log.debug("Async session closed for Auth.")
