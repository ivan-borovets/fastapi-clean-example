from dishka import Provider, Scope, provide

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.services.user import UserService
from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)
from app.infrastructure.adapters.user_id_generator_uuid import (
    UuidUserIdGenerator,
)


class DomainProvider(Provider):
    scope = Scope.REQUEST

    # Services
    user_service = provide(source=UserService)

    # Ports
    password_hasher = provide(
        source=BcryptPasswordHasher,
        provides=PasswordHasher,
    )
    user_id_generator = provide(
        source=UuidUserIdGenerator,
        provides=UserIdGenerator,
    )
