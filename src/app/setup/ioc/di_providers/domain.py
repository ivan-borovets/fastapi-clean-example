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


class UserDomainProvider(Provider):
    scope = Scope.REQUEST

    # Services
    user_service = provide(source=UserService)

    # Ports
    user_id_generator = provide(
        source=UuidUserIdGenerator,
        provides=UserIdGenerator,
    )
    password_hasher = provide(
        source=BcryptPasswordHasher,
        provides=PasswordHasher,
    )
