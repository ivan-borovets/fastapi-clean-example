from dishka import Provider, Scope, provide

from app.config.settings import PasswordHasherSettings
from app.core.commands.activate_user import ActivateUser
from app.core.commands.create_user import CreateUser
from app.core.commands.deactivate_user import DeactivateUser
from app.core.commands.grant_admin import GrantAdmin
from app.core.commands.ports.flusher import Flusher
from app.core.commands.ports.transaction_manager import TransactionManager
from app.core.commands.ports.user_tx_storage import UserTxStorage
from app.core.commands.ports.utc_timer import UtcTimer
from app.core.commands.revoke_admin import RevokeAdmin
from app.core.commands.set_user_password import SetUserPassword
from app.core.common.authorization.current_user_service import CurrentUserService
from app.core.common.authorization.ports import AuthzUserFinder
from app.core.common.ports.access_revoker import AccessRevoker
from app.core.common.ports.identity_provider import IdentityProvider
from app.core.common.ports.password_hasher import PasswordHasher
from app.core.common.services.user import UserService
from app.core.queries.list_users import ListUsers
from app.core.queries.ports.user_reader import UserReader
from app.infrastructure.adapters.auth_session_access_revoker import AuthSessionAccessRevoker
from app.infrastructure.adapters.auth_session_identity_provider import AuthSessionIdentityProvider
from app.infrastructure.adapters.bcrypt_password_hasher import (
    BcryptPasswordHasher,
    HasherSemaphore,
    HasherThreadPoolExecutor,
)
from app.infrastructure.adapters.sqla_flusher import SqlaFlusher
from app.infrastructure.adapters.sqla_transaction_manager import SqlaTransactionManager
from app.infrastructure.adapters.sqla_user_reader import SqlaUserReader
from app.infrastructure.adapters.sqla_user_tx_storage import SqlaUserTxStorage
from app.infrastructure.adapters.system_utc_timer import SystemUtcTimer


class CoreProvider(Provider):
    scope = Scope.REQUEST

    # Services
    user_service = provide(UserService, scope=Scope.APP)
    current_user_service = provide(CurrentUserService)

    # Common Ports
    @provide(scope=Scope.APP)
    def provide_password_hasher(
        self,
        settings: PasswordHasherSettings,
        executor: HasherThreadPoolExecutor,
        semaphore: HasherSemaphore,
    ) -> PasswordHasher:
        return BcryptPasswordHasher(
            pepper=settings.PEPPER.encode(),
            work_factor=settings.WORK_FACTOR,
            executor=executor,
            semaphore=semaphore,
            semaphore_wait_timeout_s=settings.SEMAPHORE_WAIT_TIMEOUT_S,
        )

    identity_provider = provide(AuthSessionIdentityProvider, provides=IdentityProvider)
    authz_user_finder = provide(SqlaUserTxStorage, provides=AuthzUserFinder)
    access_revoker = provide(AuthSessionAccessRevoker, provides=AccessRevoker)

    # Commands Ports
    utc_timer = provide(SystemUtcTimer, provides=UtcTimer)
    user_tx_storage = provide(SqlaUserTxStorage, provides=UserTxStorage)
    flusher = provide(SqlaFlusher, provides=Flusher)
    tx_manager = provide(SqlaTransactionManager, provides=TransactionManager)

    # Commands
    create_user = provide(CreateUser)
    set_user_password = provide(SetUserPassword)
    grant_admin = provide(GrantAdmin)
    revoke_admin = provide(RevokeAdmin)
    activate_user = provide(ActivateUser)
    deactivate_user = provide(DeactivateUser)

    # Query Ports
    user_reader = provide(SqlaUserReader, provides=UserReader)

    # Queries
    list_users = provide(ListUsers)
