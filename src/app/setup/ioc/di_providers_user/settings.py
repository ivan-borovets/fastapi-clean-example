from dishka import Provider, Scope, provide

from app.infrastructure.custom_types import PasswordPepper
from app.setup.config.settings import Settings
from app.setup.ioc.enum_component import ComponentEnum


class UserSettingsProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.APP

    @provide
    def provide_password_pepper(self, settings: Settings) -> PasswordPepper:
        return PasswordPepper(settings.security.password.pepper)
