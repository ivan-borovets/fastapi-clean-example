# pylint: disable=C0301 (line-too-long)

import logging
from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.common.b_application.persistence.committer import Committer
from app.common.c_infrastructure.custom_types import PostgresDsn
from app.common.c_infrastructure.persistence.sqla.committer import SqlaCommitter
from app.setup.config.settings import SqlaEngineSettings

log = logging.getLogger(__name__)


class CommonInfrastructureProvider(Provider):
    committer = provide(
        source=SqlaCommitter,
        scope=Scope.REQUEST,
        provides=Committer,
    )

    @provide(scope=Scope.APP)
    async def provide_async_engine(
        self,
        dsn: PostgresDsn,
        engine_settings: SqlaEngineSettings,
    ) -> AsyncIterable[AsyncEngine]:
        async_engine_params = {
            "url": dsn,
            **engine_settings.model_dump(),
        }
        async_engine = create_async_engine(**async_engine_params)
        log.debug("Async engine created with DSN: %s", dsn)
        yield async_engine
        log.debug("Disposing async engine...")
        await async_engine.dispose()
        log.debug("Engine is disposed.")

    @provide(scope=Scope.APP)
    def provide_async_session_maker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
        )
        log.debug("Session provider is initialized.")
        return session_factory

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(
        self,
        async_session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        log.debug("Starting async session...")
        async with async_session_maker() as session:
            log.debug("Async session created.")
            yield session
            log.debug("Closing async session.")
