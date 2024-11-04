# pylint: disable=C0301 (line-too-long)
from typing import Annotated, Mapping

from dishka import FromComponent, Provider, Scope, provide, provide_all

from app.application.admin_create_user import CreateUserInteractor
from app.application.admin_grant_admin import GrantAdminInteractor
from app.application.admin_inactivate_user import InactivateUserInteractor
from app.application.admin_list_users import ListUsersInteractor
from app.application.admin_reactivate_user import ReactivateUserInteractor
from app.application.admin_revoke_admin import RevokeAdminInteractor
from app.application.common.authorization.config import (
    ROLE_HIERARCHY,
    ROLE_PERMISSIONS,
    PermissionEnum,
)
from app.application.common.authorization.role_permission_resolver import (
    RolePermissionResolver,
)
from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.committer import Committer
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.user_data_gateway import UserDataGateway
from app.application.user_change_password import ChangePasswordInteractor
from app.domain.entities.user.role_enum import UserRoleEnum
from app.infrastructure.adapters.application.sqla_committer import SqlaCommitter
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.session_context.common.application_adapters.session_access_revoker import (
    SessionAccessRevoker,
)
from app.infrastructure.session_context.common.application_adapters.session_identity_provider import (
    SessionIdentityProvider,
)
from app.infrastructure.session_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.session_context.common.managers.session import SessionManager
from app.infrastructure.session_context.common.sqla_session_data_mapper import (
    SqlaSessionDataMapper,
)
from app.setup.ioc.di_component_enum import ComponentEnum


class UserApplicationServicesProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

    @provide
    def provide_role_hierarchy(
        self,
    ) -> Mapping[UserRoleEnum, set[UserRoleEnum]]:
        return ROLE_HIERARCHY

    @provide
    def provide_role_permissions(
        self,
    ) -> Mapping[UserRoleEnum, set[PermissionEnum]]:
        return ROLE_PERMISSIONS

    role_permissions_resolver = provide(source=RolePermissionResolver)
    authorization_service = provide(source=AuthorizationService)


class UserApplicationPortsProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

    committer = provide(
        source=SqlaCommitter,
        provides=Committer,
    )

    @provide
    def provide_identity_provider(
        self,
        jwt_token_manager: Annotated[
            JwtTokenManager,
            FromComponent(ComponentEnum.SESSION),
        ],
        session_manager: Annotated[
            SessionManager,
            FromComponent(ComponentEnum.SESSION),
        ],
    ) -> IdentityProvider:
        return SessionIdentityProvider(
            jwt_token_manager,
            session_manager,
        )

    @provide
    def provide_access_revoker(
        self,
        sqla_session_data_mapper: Annotated[
            SqlaSessionDataMapper,
            FromComponent(ComponentEnum.SESSION),
        ],
        sqla_committer: Annotated[
            SqlaCommitter,
            FromComponent(ComponentEnum.SESSION),
        ],
    ) -> AccessRevoker:
        return SessionAccessRevoker(sqla_session_data_mapper, sqla_committer)


class UserApplicationDataGatewaysProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

    user_data_gateway = provide(
        source=SqlaUserDataMapper,
        provides=UserDataGateway,
    )
    sqla_user_data_mapper = provide(source=SqlaUserDataMapper)


class UserApplicationInteractorsProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

    interactors = provide_all(
        CreateUserInteractor,
        GrantAdminInteractor,
        InactivateUserInteractor,
        ListUsersInteractor,
        ReactivateUserInteractor,
        RevokeAdminInteractor,
        ChangePasswordInteractor,
    )
