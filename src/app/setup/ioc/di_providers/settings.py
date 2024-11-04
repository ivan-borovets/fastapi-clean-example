import logging

from dishka import Provider, Scope, from_context, provide
from dishka.dependency_source.composite import CompositeDependencySource

from app.common.c_infrastructure.custom_types import (
    JwtAccessTokenTtlMin,
    JwtAlgorithm,
    JwtSecret,
    PasswordPepper,
    PostgresDsn,
    SessionRefreshThreshold,
)
from app.setup.config.cookie_params import CookieParams
from app.setup.config.settings import Settings, SqlaEngineSettings

log = logging.getLogger(__name__)


class SettingsProvider(Provider):
    settings: CompositeDependencySource = from_context(
        provides=Settings, scope=Scope.RUNTIME
    )

    @provide(scope=Scope.APP)
    def provide_password_pepper(self, settings: Settings) -> PasswordPepper:
        return PasswordPepper(settings.security.password.pepper)

    @provide(scope=Scope.APP)
    def provide_jwt_secret(self, settings: Settings) -> JwtSecret:
        return JwtSecret(settings.security.session.jwt_secret)

    @provide(scope=Scope.APP)
    def provide_jwt_algorithm(self, settings: Settings) -> JwtAlgorithm:
        return settings.security.session.jwt_algorithm

    @provide(scope=Scope.APP)
    def provide_jwt_access_token_ttl_min(
        self, settings: Settings
    ) -> JwtAccessTokenTtlMin:
        return JwtAccessTokenTtlMin(settings.security.session.session_ttl_min)

    @provide(scope=Scope.APP)
    def provide_session_refresh_threshold(
        self, settings: Settings
    ) -> SessionRefreshThreshold:
        return SessionRefreshThreshold(
            settings.security.session.session_refresh_threshold
        )

    @provide(scope=Scope.APP)
    def provide_cookie_params(self, settings: Settings) -> CookieParams:
        is_cookies_secure: bool = settings.security.cookies.secure
        if is_cookies_secure:
            return CookieParams(secure=True, samesite="strict")
        return CookieParams(secure=False)

    @provide(scope=Scope.APP)
    def provide_postgres_dsn(self, settings: Settings) -> PostgresDsn:
        return PostgresDsn(settings.db.postgres.dsn)

    @provide(scope=Scope.APP)
    def provide_sqla_engine_settings(self, settings: Settings) -> SqlaEngineSettings:
        return settings.db.sqla_engine
