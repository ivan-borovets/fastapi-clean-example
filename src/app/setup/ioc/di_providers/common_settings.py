# pylint: disable=C0301 (line-too-long)

import logging
from typing import NewType

from dishka import Provider, Scope, from_context, provide

from app.setup.config.settings import AppSettings, SqlaEngineSettings
from app.setup.ioc.di_component_enum import ComponentEnum

PostgresDsn = NewType("PostgresDsn", str)

log = logging.getLogger(__name__)


class CommonSettingsProvider(Provider):
    component = ComponentEnum.DEFAULT

    settings = from_context(provides=AppSettings, scope=Scope.RUNTIME)

    @provide(scope=Scope.APP)
    def provide_postgres_dsn(self, settings: AppSettings) -> PostgresDsn:
        return PostgresDsn(settings.postgres.dsn)

    @provide(scope=Scope.APP)
    def provide_sqla_engine_settings(self, settings: AppSettings) -> SqlaEngineSettings:
        return settings.sqla
