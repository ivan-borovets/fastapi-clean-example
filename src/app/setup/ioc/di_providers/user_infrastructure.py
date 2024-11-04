# pylint: disable=C0301 (line-too-long)

import logging
from typing import Annotated, AsyncIterable

from dishka import FromComponent, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.setup.ioc.di_component_enum import ComponentEnum

log = logging.getLogger(__name__)


class UserInfrastructureProvider(Provider):
    component = ComponentEnum.USER

    @provide(scope=Scope.APP)
    def provide_async_session_maker(
        self,
        engine: Annotated[
            AsyncEngine,
            FromComponent(ComponentEnum.DEFAULT),
        ],
    ) -> async_sessionmaker[AsyncSession]:
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
            info={
                "component": self.component,
            },
        )
        log.debug("Async session maker initialized.")
        return session_factory

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(
        self,
        async_session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        log.debug("Starting async session...")
        async with async_session_maker() as session:
            log.debug("Async session started for '%s'.", self.component)
            yield session
            log.debug("Closing async session.")
        log.debug("Async session closed for '%s'.", self.component)
