# pylint: disable=C0301 (line-too-long)
from typing import Annotated

from dishka import FromComponent, Provider, Scope, from_context, provide, provide_all
from starlette.requests import Request

from app.domain.user.service import UserService
from app.infrastructure.persistence.sqla.committer import SqlaCommitter
from app.infrastructure.session.access_token_processor_jwt import (
    JwtAccessTokenProcessor,
)
from app.infrastructure.session.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)
from app.infrastructure.session.scenarios.log_in.interactor import LogInInteractor
from app.infrastructure.session.scenarios.log_out.interactor import LogOutInteractor
from app.infrastructure.session.services.jwt_token import JwtTokenService
from app.infrastructure.session.services.session import SessionService
from app.infrastructure.session.session_data_mapper_sqla import SqlaSessionDataMapper
from app.infrastructure.session.session_id_generator_str import StrSessionIdGenerator
from app.infrastructure.session.session_timer_utc import UtcSessionTimer
from app.infrastructure.user.adapters_application.identity_provider_session import (
    SessionIdentityProvider,
)
from app.infrastructure.user.adapters_application.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)
from app.presentation.session.adapters_infrastructure.access_token_request_handler_cookie import (
    CookieAccessTokenRequestHandler,
)
from app.setup.ioc.enum_component import ComponentEnum


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
        SessionService,
        StrSessionIdGenerator,
        UtcSessionTimer,
        SqlaCommitter,
        JwtTokenService,
        JwtAccessTokenProcessor,
    )

    @provide
    def provide_session_identity_provider(
        self,
        jwt_token_service: JwtTokenService,
        session_service: SessionService,
    ) -> SessionIdentityProvider:
        return SessionIdentityProvider(
            jwt_token_service,
            session_service,
        )


class SessionInfraInteractorProvider(Provider):
    component = ComponentEnum.SESSION
    scope = Scope.REQUEST

    @provide
    def provide_login_interactor(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
        session_service: SessionService,
        jtw_token_service: JwtTokenService,
        user_service: Annotated[
            UserService,
            FromComponent(ComponentEnum.USER),
        ],
    ) -> LogInInteractor:
        return LogInInteractor(
            session_identity_provider,
            sqla_user_data_mapper,
            session_service,
            jtw_token_service,
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
        session_service: SessionService,
        jtw_token_service: JwtTokenService,
    ) -> LogOutInteractor:
        return LogOutInteractor(
            session_identity_provider,
            sqla_user_data_mapper,
            session_service,
            jtw_token_service,
        )
