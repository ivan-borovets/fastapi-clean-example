# pylint: disable=C0301 (line-too-long)
import logging
from typing import Annotated, AsyncIterable

from dishka import FromComponent, Provider, Scope, from_context, provide, provide_all
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.requests import Request

from app.domain.services.user import UserService
from app.infrastructure.adapters.application.sqla_transaction_manager import (
    SqlaTransactionManager,
)
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.auth_context.common.application_adapters.auth_session_identity_provider import (
    AuthSessionIdentityProvider,
)
from app.infrastructure.auth_context.common.jwt_access_token_processor import (
    JwtAccessTokenProcessor,
)
from app.infrastructure.auth_context.common.managers.auth_session import (
    AuthSessionManager,
)
from app.infrastructure.auth_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.auth_context.common.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)
from app.infrastructure.auth_context.common.sqla_auth_session_data_mapper import (
    SqlaAuthSessionDataMapper,
)
from app.infrastructure.auth_context.common.str_auth_session_id_generator import (
    StrAuthSessionIdGenerator,
)
from app.infrastructure.auth_context.common.utc_auth_session_timer import (
    UtcAuthSessionTimer,
)
from app.infrastructure.auth_context.log_in import LogInHandler
from app.infrastructure.auth_context.log_out import LogOutHandler
from app.infrastructure.auth_context.sign_up import SignUpHandler
from app.presentation.common.infrastructure_adapters.auth_context.cookie_access_token_request_handler import (
    CookieAccessTokenRequestHandler,
)
from app.setup.ioc.di_component_enum import ComponentEnum

log = logging.getLogger(__name__)


class AuthInfrastructureProvider(Provider):
    component = ComponentEnum.AUTH

    # Connection
    @provide(scope=Scope.APP)
    def provide_async_session_maker(
        self,
        engine: Annotated[
            AsyncEngine,
            FromComponent(ComponentEnum.DEFAULT),
        ],
    ) -> async_sessionmaker[AsyncSession]:
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
            info={
                "component": self.component,
            },
        )
        log.debug("Async session maker initialized.")
        return session_factory

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(
        self,
        async_session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        log.debug("Starting async session...")
        async with async_session_maker() as session:
            log.debug("Async session started for '%s'.", self.component)
            yield session
            log.debug("Closing async session.")
        log.debug("Async session closed for '%s'.", self.component)

    # Ports
    request = from_context(provides=Request, scope=Scope.REQUEST)

    access_token_request_handler = provide(
        source=CookieAccessTokenRequestHandler,
        provides=AccessTokenRequestHandler,
        scope=Scope.REQUEST,
    )

    # Data Mappers
    sqla_auth_session_data_mapper = provide(
        source=SqlaAuthSessionDataMapper,
        scope=Scope.REQUEST,
    )

    # Concrete Objects
    infra_objects = provide_all(
        AuthSessionManager,
        StrAuthSessionIdGenerator,
        UtcAuthSessionTimer,
        SqlaTransactionManager,
        JwtTokenManager,
        JwtAccessTokenProcessor,
        AuthSessionIdentityProvider,
        scope=Scope.REQUEST,
    )

    # "Interactors" (Infrastructure handlers)
    @provide(scope=Scope.REQUEST)
    def provide_sign_up_handler(
        self,
        auth_session_identity_provider: AuthSessionIdentityProvider,
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
        user_service: Annotated[
            UserService,
            FromComponent(ComponentEnum.USER),
        ],
        sqla_transaction_manager: Annotated[
            SqlaTransactionManager,
            FromComponent(ComponentEnum.USER),
        ],
    ) -> SignUpHandler:
        return SignUpHandler(
            auth_session_identity_provider,
            sqla_user_data_mapper,
            user_service,
            sqla_transaction_manager,
        )

    @provide(scope=Scope.REQUEST)
    def provide_login_handler(
        self,
        auth_session_identity_provider: AuthSessionIdentityProvider,
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
        auth_session_manager: AuthSessionManager,
        jtw_token_manager: JwtTokenManager,
        user_service: Annotated[
            UserService,
            FromComponent(ComponentEnum.USER),
        ],
        sqla_transaction_manager: SqlaTransactionManager,
    ) -> LogInHandler:
        return LogInHandler(
            auth_session_identity_provider,
            sqla_user_data_mapper,
            auth_session_manager,
            jtw_token_manager,
            user_service,
            sqla_transaction_manager,
        )

    @provide(scope=Scope.REQUEST)
    def provide_logout_handler(
        self,
        auth_session_identity_provider: AuthSessionIdentityProvider,
        sqla_user_data_mapper: Annotated[
            SqlaUserDataMapper,
            FromComponent(ComponentEnum.USER),
        ],
        auth_session_manager: AuthSessionManager,
        jtw_token_manager: JwtTokenManager,
        sqla_transaction_manager: SqlaTransactionManager,
    ) -> LogOutHandler:
        return LogOutHandler(
            auth_session_identity_provider,
            sqla_user_data_mapper,
            auth_session_manager,
            jtw_token_manager,
            sqla_transaction_manager,
        )
