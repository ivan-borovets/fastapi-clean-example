# pylint: disable=C0301 (line-too-long)
from typing import Annotated

from dishka import FromComponent, Provider, Scope, from_context, provide, provide_all
from starlette.requests import Request

from app.application.common.ports.committer import Committer
from app.domain.user.service import UserService
from app.infrastructure.adapters.application.sqla_committer import SqlaCommitter
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.session_context.common.application_adapters.session_identity_provider import (
    SessionIdentityProvider,
)
from app.infrastructure.session_context.common.jwt_access_token_processor import (
    JwtAccessTokenProcessor,
)
from app.infrastructure.session_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.session_context.common.managers.session import SessionManager
from app.infrastructure.session_context.common.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)
from app.infrastructure.session_context.common.sqla_session_data_mapper import (
    SqlaSessionDataMapper,
)
from app.infrastructure.session_context.common.str_session_id_generator import (
    StrSessionIdGenerator,
)
from app.infrastructure.session_context.common.utc_session_timer import UtcSessionTimer
from app.infrastructure.session_context.log_in import LogInInteractor
from app.infrastructure.session_context.log_out import LogOutInteractor
from app.infrastructure.session_context.sign_up import SignUpInteractor
from app.presentation.common.infrastructure_adapters.session_context.cookie_access_token_request_handler import (
    CookieAccessTokenRequestHandler,
)
from app.setup.ioc.di_component_enum import ComponentEnum


class SessionInfraPortsProvider(Provider):
    component = ComponentEnum.SESSION
    scope = Scope.REQUEST

    request = from_context(provides=Request)

    access_token_request_handler = provide(
        source=CookieAccessTokenRequestHandler,
        provides=AccessTokenRequestHandler,
    )


class SessionInfraDataMappersProvider(Provider):
    component = ComponentEnum.SESSION
    scope = Scope.REQUEST

    sqla_session_data_mapper = provide(
        source=SqlaSessionDataMapper,
        scope=Scope.REQUEST,
    )


class SessionInfraConcreteProvider(Provider):
    component = ComponentEnum.SESSION
    scope = Scope.REQUEST

    infra_objects = provide_all(
        SessionManager,
        StrSessionIdGenerator,
        UtcSessionTimer,
        SqlaCommitter,
        JwtTokenManager,
        JwtAccessTokenProcessor,
        SessionIdentityProvider,
    )


class SessionInfraInteractorProvider(Provider):
    component = ComponentEnum.SESSION
    scope = Scope.REQUEST

    @provide
    def provide_sign_up_interactor(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
        user_service: Annotated[
            UserService,
            FromComponent(ComponentEnum.USER),
        ],
        committer: Annotated[
            Committer,
            FromComponent(ComponentEnum.USER),
        ],
    ) -> SignUpInteractor:
        return SignUpInteractor(
            session_identity_provider,
            sqla_user_data_mapper,
            user_service,
            committer,
        )

    @provide
    def provide_login_interactor(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
        session_manager: SessionManager,
        jtw_token_manager: JwtTokenManager,
        user_service: Annotated[
            UserService,
            FromComponent(ComponentEnum.USER),
        ],
    ) -> LogInInteractor:
        return LogInInteractor(
            session_identity_provider,
            sqla_user_data_mapper,
            session_manager,
            jtw_token_manager,
            user_service,
        )

    @provide
    def provide_logout_interactor(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
        session_manager: SessionManager,
        jtw_token_manager: JwtTokenManager,
    ) -> LogOutInteractor:
        return LogOutInteractor(
            session_identity_provider,
            sqla_user_data_mapper,
            session_manager,
            jtw_token_manager,
        )
