# pylint: disable=C0301 (line-too-long)

from dishka import Provider, Scope, provide

from app.domain.user.ports.password_hasher import PasswordHasher
from app.domain.user.ports.user_id_generator import UserIdGenerator
from app.domain.user.service import UserService
from app.infrastructure.user.adapters_domain.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)
from app.infrastructure.user.adapters_domain.user_id_generator_uuid import (
    UuidUserIdGenerator,
)
from app.setup.ioc.enum_component import ComponentEnum


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
