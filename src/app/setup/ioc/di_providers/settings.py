from dishka import Provider, Scope, from_context, provide

from app.infrastructure.adapters.password_hasher_bcrypt import PasswordPepper
from app.infrastructure.auth.session.timer_utc import (
    AuthSessionRefreshThreshold,
    AuthSessionTtlMin,
)
from app.infrastructure.persistence_sqla.config import PostgresDsn, SqlaEngineConfig
from app.presentation.http.auth.access_token_processor_jwt import (
    JwtAlgorithm,
    JwtSecret,
)
from app.presentation.http.auth.cookie_params import CookieParams
from app.setup.config.settings import AppSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    settings = from_context(provides=AppSettings)

    @provide
    def provide_postgres_dsn(self, settings: AppSettings) -> PostgresDsn:
        return PostgresDsn(settings.postgres.dsn)

    @provide
    def provide_sqla_engine_config(self, settings: AppSettings) -> SqlaEngineConfig:
        return SqlaEngineConfig(**settings.sqla.model_dump())

    @provide
    def provide_password_pepper(self, settings: AppSettings) -> PasswordPepper:
        return PasswordPepper(settings.security.password.pepper)

    @provide
    def provide_jwt_secret(self, settings: AppSettings) -> JwtSecret:
        return JwtSecret(settings.security.auth.jwt_secret)

    @provide
    def provide_jwt_algorithm(self, settings: AppSettings) -> JwtAlgorithm:
        return settings.security.auth.jwt_algorithm

    @provide
    def provide_auth_session_ttl_min(self, settings: AppSettings) -> AuthSessionTtlMin:
        return AuthSessionTtlMin(settings.security.auth.session_ttl_min)

    @provide
    def provide_auth_session_refresh_threshold(
        self,
        settings: AppSettings,
    ) -> AuthSessionRefreshThreshold:
        return AuthSessionRefreshThreshold(
            settings.security.auth.session_refresh_threshold,
        )

    @provide
    def provide_cookie_params(self, settings: AppSettings) -> CookieParams:
        return CookieParams(secure=settings.security.cookies.secure)
