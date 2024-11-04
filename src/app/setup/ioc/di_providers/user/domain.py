# pylint: disable=C0301 (line-too-long)

from dishka import Provider, Scope, provide

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.services.user import UserService
from app.infrastructure.adapters.domain.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from app.infrastructure.adapters.domain.uuid_user_id_generator import (
    UuidUserIdGenerator,
)
from app.setup.ioc.di_component_enum import ComponentEnum


class UserDomainServicesProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

    user_service = provide(source=UserService)


class UserDomainPortsProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

    user_id_generator = provide(
        source=UuidUserIdGenerator,
        provides=UserIdGenerator,
    )
    password_hasher = provide(
        source=BcryptPasswordHasher,
        provides=PasswordHasher,
    )
