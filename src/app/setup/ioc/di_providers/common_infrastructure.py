# pylint: disable=C0301 (line-too-long)

import logging
from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.setup.config.settings import SqlaEngineSettings
from app.setup.ioc.di_component_enum import ComponentEnum
from app.setup.ioc.di_providers.common_settings import PostgresDsn

log = logging.getLogger(__name__)


class CommonInfrastructureProvider(Provider):
    component = ComponentEnum.DEFAULT
    scope = Scope.APP

    @provide
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
