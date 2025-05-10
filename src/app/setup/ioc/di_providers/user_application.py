# pylint: disable=C0301 (line-too-long)
from typing import Annotated

from dishka import FromComponent, Provider, Scope, provide, provide_all

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
from app.infrastructure.adapters.application.sqla_transaction_manager import (
    SqlaTransactionManager,
)
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.application.sqla_user_reader import SqlaUserReader
from app.infrastructure.auth_context.common.application_adapters.auth_session_access_revoker import (
    AuthSessionAccessRevoker,
)
from app.infrastructure.auth_context.common.application_adapters.auth_session_identity_provider import (
    AuthSessionIdentityProvider,
)
from app.infrastructure.auth_context.common.managers.auth_session import (
    AuthSessionManager,
)
from app.infrastructure.auth_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.auth_context.common.sqla_auth_session_data_mapper import (
    SqlaAuthSessionDataMapper,
)
from app.setup.ioc.di_component_enum import ComponentEnum


class UserApplicationProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

    # Services
    authorization_service = provide(source=AuthorizationService)
    current_user_service = provide(source=CurrentUserService)

    # Ports
    transaction_manager = provide(
        source=SqlaTransactionManager,
        provides=TransactionManager,
    )
    sqla_transaction_manager = provide(
        source=SqlaTransactionManager,
    )

    @provide
    def provide_identity_provider(
        self,
        jwt_token_manager: Annotated[
            JwtTokenManager,
            FromComponent(ComponentEnum.AUTH),
        ],
        auth_session_manager: Annotated[
            AuthSessionManager,
            FromComponent(ComponentEnum.AUTH),
        ],
        sqla_transaction_manager: Annotated[
            SqlaTransactionManager,
            FromComponent(ComponentEnum.AUTH),
        ],
    ) -> IdentityProvider:
        return AuthSessionIdentityProvider(
            jwt_token_manager,
            auth_session_manager,
            sqla_transaction_manager,
        )

    @provide
    def provide_access_revoker(
        self,
        sqla_auth_session_data_mapper: Annotated[
            SqlaAuthSessionDataMapper,
            FromComponent(ComponentEnum.AUTH),
        ],
        transaction_manager: Annotated[
            SqlaTransactionManager,
            FromComponent(ComponentEnum.AUTH),
        ],
    ) -> AccessRevoker:
        return AuthSessionAccessRevoker(
            sqla_auth_session_data_mapper,
            transaction_manager,
        )

    # Command Gateways
    user_command_gateway = provide(
        source=SqlaUserDataMapper,
        provides=UserCommandGateway,
    )
    sqla_user_data_mapper = provide(source=SqlaUserDataMapper)

    # Query Gateways
    user_query_gateway = provide(
        source=SqlaUserReader,
        provides=UserQueryGateway,
    )
    sqla_user_reader = provide(SqlaUserReader)

    # Interactors
    interactors = provide_all(
        CreateUserInteractor,
        GrantAdminInteractor,
        InactivateUserInteractor,
        ReactivateUserInteractor,
        RevokeAdminInteractor,
        ChangePasswordInteractor,
    )

    # Query Services
    query_services = provide_all(
        ListUsersQueryService,
    )
