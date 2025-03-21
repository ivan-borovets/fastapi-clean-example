from dishka import Provider, Scope, provide

from app.infrastructure.new_types import PasswordPepper
from app.setup.config.settings import AppSettings
from app.setup.ioc.di_component_enum import ComponentEnum


class UserSettingsProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.APP

    @provide
    def provide_password_pepper(self, settings: AppSettings) -> PasswordPepper:
        return PasswordPepper(settings.security.password.pepper)
