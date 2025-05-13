# pylint: disable=C0301 (line-too-long)
from dishka import Provider, Scope, provide, provide_all

from app.application.commands.admin_create_user import CreateUserInteractor
from app.application.commands.admin_inactivate_user import InactivateUserInteractor
from app.application.commands.admin_reactivate_user import ReactivateUserInteractor
from app.application.commands.super_admin_grant_admin import GrantAdminInteractor
from app.application.commands.super_admin_revoke_admin import RevokeAdminInteractor
from app.application.commands.user_change_password import ChangePasswordInteractor
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.query_gateways.user import UserQueryGateway
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.application.queries.admin_list_users import ListUsersQueryService
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.application.sqla_user_reader import SqlaUserReader
from app.infrastructure.adapters.application.sqla_user_transaction_manager import (
    SqlaUserTransactionManager,
)
from app.infrastructure.auth_context.common.application_adapters.auth_session_access_revoker import (
    AuthSessionAccessRevoker,
)
from app.infrastructure.auth_context.common.application_adapters.auth_session_identity_provider import (
    AuthSessionIdentityProvider,
)


class UserApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Services
    services = provide_all(
        AuthorizationService,
        CurrentUserService,
    )

    # Ports
    user_transaction_manager = provide(
        source=SqlaUserTransactionManager,
        provides=TransactionManager,
    )
    auth_session_identity_provider = provide(
        source=AuthSessionIdentityProvider,
        provides=IdentityProvider,
    )
    access_revoker = provide(
        source=AuthSessionAccessRevoker,
        provides=AccessRevoker,
    )

    # Gateways
    user_command_gateway = provide(
        source=SqlaUserDataMapper,
        provides=UserCommandGateway,
    )
    user_query_gateway = provide(
        source=SqlaUserReader,
        provides=UserQueryGateway,
    )

    # Interactors
    interactors = provide_all(
        CreateUserInteractor,
        GrantAdminInteractor,
        InactivateUserInteractor,
        ReactivateUserInteractor,
        RevokeAdminInteractor,
        ChangePasswordInteractor,
    )
    query_services = provide_all(
        ListUsersQueryService,
    )
