# pylint: disable=C0301 (line-too-long)
from typing import Annotated

from dishka import FromComponent, Provider, Scope, provide, provide_all

from app.application.committer import Committer
from app.application.user.ports.global_logout_service import GlobalLogoutService
from app.application.user.ports.identity_provider import IdentityProvider
from app.application.user.ports.user_data_gateway import UserDataGateway
from app.application.user.service_authorization import AuthorizationService
from app.application_scenarios.account_sign_up.interactor import SignUpInteractor
from app.application_scenarios.admin_create_user.interactor import CreateUserInteractor
from app.application_scenarios.admin_grant_admin.interactor import GrantAdminInteractor
from app.application_scenarios.admin_inactivate_user.interactor import (
    InactivateUserInteractor,
)
from app.application_scenarios.admin_list_users.interactor import ListUsersInteractor
from app.application_scenarios.admin_reactivate_user.interactor import (
    ReactivateUserInteractor,
)
from app.application_scenarios.admin_revoke_admin.interactor import (
    RevokeAdminInteractor,
)
from app.infrastructure.adapters_application.global_logout_service_session import (
    SessionGlobalLogoutService,
)
from app.infrastructure.adapters_application.identity_provider_session import (
    SessionIdentityProvider,
)
from app.infrastructure.adapters_application.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)
from app.infrastructure.persistence.sqla.committer import SqlaCommitter
from app.infrastructure.session.services.jwt_token import JwtTokenService
from app.infrastructure.session.services.session import SessionService
from app.infrastructure.session.session_data_mapper_sqla import SqlaSessionDataMapper
from app.setup.ioc.enum_component import ComponentEnum


class UserApplicationServicesProvider(Provider):
    component = ComponentEnum.USER
    scope = Scope.REQUEST

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
        jwt_token_service: Annotated[
            JwtTokenService,
            FromComponent(ComponentEnum.SESSION),
        ],
        session_service: Annotated[
            SessionService,
            FromComponent(ComponentEnum.SESSION),
        ],
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
    ) -> IdentityProvider:
        return SessionIdentityProvider(
            jwt_token_service, session_service, sqla_user_data_mapper
        )

    @provide
    def provide_global_logout_service(
        self,
        sqla_session_data_mapper: Annotated[
            SqlaSessionDataMapper,
            FromComponent(ComponentEnum.SESSION),
        ],
        sqla_committer: Annotated[
            SqlaCommitter,
            FromComponent(ComponentEnum.SESSION),
        ],
    ) -> GlobalLogoutService:
        return SessionGlobalLogoutService(sqla_session_data_mapper, sqla_committer)


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
        SignUpInteractor,
        CreateUserInteractor,
        GrantAdminInteractor,
        InactivateUserInteractor,
        ListUsersInteractor,
        ReactivateUserInteractor,
        RevokeAdminInteractor,
    )
