from dishka import Provider, Scope, provide, provide_all

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.services.user import UserService
from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)
from app.infrastructure.adapters.types import HasherSemaphore, HasherThreadPoolExecutor
from app.infrastructure.adapters.user_id_generator_uuid import (
    UuidUserIdGenerator,
)
from app.setup.config.security import SecuritySettings


class DomainProvider(Provider):
    scope = Scope.APP

    # Services
    user_service = provide_all(
        UserService,
    )

    # Ports
    user_id_generator = provide(UuidUserIdGenerator, provides=UserIdGenerator)

    @provide
    def provide_password_hasher(
        self,
        security: SecuritySettings,
        executor: HasherThreadPoolExecutor,
        semaphore: HasherSemaphore,
    ) -> PasswordHasher:
        return BcryptPasswordHasher(
            pepper=security.password.pepper.encode(),
            work_factor=security.password.hasher_work_factor,
            executor=executor,
            semaphore=semaphore,
            semaphore_wait_timeout_s=security.password.hasher_semaphore_wait_timeout_s,
        )
