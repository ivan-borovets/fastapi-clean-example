# pylint: disable=C0301 (line-too-long)

import logging
from typing import NewType

from dishka import Provider, Scope, from_context, provide

from app.setup.config.settings import Settings, SqlaEngineSettings
from app.setup.ioc.di_component_enum import ComponentEnum

PostgresDsn = NewType("PostgresDsn", str)

log = logging.getLogger(__name__)


class CommonSettingsProvider(Provider):
    component = ComponentEnum.DEFAULT

    settings = from_context(provides=Settings, scope=Scope.RUNTIME)

    @provide(scope=Scope.APP)
    def provide_postgres_dsn(self, settings: Settings) -> PostgresDsn:
        return PostgresDsn(settings.db.postgres.dsn)

    @provide(scope=Scope.APP)
    def provide_sqla_engine_settings(self, settings: Settings) -> SqlaEngineSettings:
        return settings.db.sqla_engine
