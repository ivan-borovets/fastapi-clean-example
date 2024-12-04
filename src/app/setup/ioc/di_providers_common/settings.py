# pylint: disable=C0301 (line-too-long)

import logging
from typing import NewType

from dishka import Provider, Scope, from_context, provide
from dishka.dependency_source.composite import CompositeDependencySource

from app.setup.config.settings import Settings, SqlaEngineSettings
from app.setup.ioc.enum_component import ComponentEnum

PostgresDsn = NewType("PostgresDsn", str)

log = logging.getLogger(__name__)


class SettingsProvider(Provider):
    component = ComponentEnum.DEFAULT
    scope = Scope.RUNTIME

    settings: CompositeDependencySource = from_context(provides=Settings)


class CommonSettingsProvider(Provider):
    component = ComponentEnum.DEFAULT
    scope = Scope.APP

    @provide
    def provide_postgres_dsn(self, settings: Settings) -> PostgresDsn:
        return PostgresDsn(settings.db.postgres.dsn)

    @provide
    def provide_sqla_engine_settings(self, settings: Settings) -> SqlaEngineSettings:
        return settings.db.sqla_engine
