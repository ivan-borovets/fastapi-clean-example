from dishka import Provider, Scope, provide

from app.infrastructure.auth_context.common.new_types import (
    AuthSessionRefreshThreshold,
    AuthSessionTtlMin,
    JwtAlgorithm,
    JwtSecret,
)
from app.presentation.common.cookie_params import CookieParams
from app.setup.config.settings import Settings
from app.setup.ioc.di_component_enum import ComponentEnum


class AuthSettingsProvider(Provider):
    component = ComponentEnum.AUTH
    scope = Scope.APP

    @provide
    def provide_jwt_secret(self, settings: Settings) -> JwtSecret:
        return JwtSecret(settings.security.auth.jwt_secret)

    @provide
    def provide_jwt_algorithm(self, settings: Settings) -> JwtAlgorithm:
        return settings.security.auth.jwt_algorithm

    @provide
    def provide_auth_session_ttl_min(self, settings: Settings) -> AuthSessionTtlMin:
        return AuthSessionTtlMin(settings.security.auth.session_ttl_min)

    @provide
    def provide_auth_session_refresh_threshold(
        self, settings: Settings
    ) -> AuthSessionRefreshThreshold:
        return AuthSessionRefreshThreshold(
            settings.security.auth.session_refresh_threshold
        )

    @provide
    def provide_cookie_params(self, settings: Settings) -> CookieParams:
        is_cookies_secure: bool = settings.security.cookies.secure
        if is_cookies_secure:
            return CookieParams(secure=True, samesite="strict")
        return CookieParams(secure=False)
