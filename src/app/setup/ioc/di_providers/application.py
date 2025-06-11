from dishka import Provider, Scope, provide, provide_all

from app.application.commands.change_password import ChangePasswordInteractor
from app.application.commands.create_user import CreateUserInteractor
from app.application.commands.grant_admin import GrantAdminInteractor
from app.application.commands.inactivate_user import InactivateUserInteractor
from app.application.commands.reactivate_user import ReactivateUserInteractor
from app.application.commands.revoke_admin import RevokeAdminInteractor
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.application.queries.list_users import ListUsersQueryService
from app.infrastructure.adapters.main_transaction_manager_sqla import (
    SqlaMainTransactionManager,
)
from app.infrastructure.adapters.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.user_reader_sqla import SqlaUserReader
from app.infrastructure.auth_session.adapters.access_revoker import (
    AuthSessionAccessRevoker,
)
from app.infrastructure.auth_session.adapters.identity_provider import (
    AuthSessionIdentityProvider,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Services
    services = provide_all(
        AuthorizationService,
        CurrentUserService,
    )

    # Ports Auth
    access_revoker = provide(
        source=AuthSessionAccessRevoker,
        provides=AccessRevoker,
    )
    identity_provider = provide(
        source=AuthSessionIdentityProvider,
        provides=IdentityProvider,
    )

    # Ports Persistence
    tx_manager = provide(
        source=SqlaMainTransactionManager,
        provides=TransactionManager,
    )
    user_command_gateway = provide(
        source=SqlaUserDataMapper,
        provides=UserCommandGateway,
    )
    user_query_gateway = provide(
        source=SqlaUserReader,
        provides=UserQueryGateway,
    )

    # Commands
    commands = provide_all(
        CreateUserInteractor,
        GrantAdminInteractor,
        InactivateUserInteractor,
        ReactivateUserInteractor,
        RevokeAdminInteractor,
        ChangePasswordInteractor,
    )

    # Queries
    query_services = provide_all(
        ListUsersQueryService,
    )
