# pylint: disable=C0301 (line-too-long)
import logging
from typing import AsyncIterable, cast

from dishka import Provider, Scope, from_context, provide, provide_all
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.requests import Request

from app.infrastructure.adapters.application.new_types import UserAsyncSession
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.application.sqla_user_reader import SqlaUserReader
from app.infrastructure.adapters.application.sqla_user_transaction_manager import (
    SqlaUserTransactionManager,
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
from app.infrastructure.auth_context.common.new_types import AuthAsyncSession
from app.infrastructure.auth_context.common.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)
from app.infrastructure.auth_context.common.sqla_auth_session_data_mapper import (
    SqlaAuthSessionDataMapper,
)
from app.infrastructure.auth_context.common.sqla_auth_transaction_manager import (
    SqlaAuthTransactionManager,
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
from app.setup.config.settings import PostgresDsn, SqlaEngineSettings

log = logging.getLogger(__name__)


class CommonInfrastructureProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_async_engine(
        self,
        dsn: PostgresDsn,
        engine_settings: SqlaEngineSettings,
    ) -> AsyncIterable[AsyncEngine]:
        async_engine_params = {
            "url": dsn,
            **engine_settings.model_dump(),
        }
        async_engine = create_async_engine(**async_engine_params)
        log.debug("Async engine created with DSN: %s", dsn)
        yield async_engine
        log.debug("Disposing async engine...")
        await async_engine.dispose()
        log.debug("Engine is disposed.")

    @provide
    def provide_async_session_maker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
        )
        log.debug("Async session maker initialized.")
        return session_factory


class UserInfrastructureProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_user_async_session(
        self,
        async_session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[UserAsyncSession]:
        log.debug("Starting User async session...")
        async with async_session_maker() as session:
            log.debug("Async session started for User.")
            yield cast(UserAsyncSession, session)
            log.debug("Closing async session.")
        log.debug("Async session closed for User.")


class AuthInfrastructureProvider(Provider):
    scope = Scope.REQUEST

    # Database
    @provide
    async def provide_auth_async_session(
        self,
        async_session_maker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AuthAsyncSession]:
        log.debug("Starting Auth async session...")
        async with async_session_maker() as session:
            log.debug("Async session started for Auth.")
            yield cast(AuthAsyncSession, session)
            log.debug("Closing async session.")
        log.debug("Async session closed for Auth.")

    # Request
    request = from_context(provides=Request)

    # Ports
    access_token_request_handler = provide(
        source=CookieAccessTokenRequestHandler,
        provides=AccessTokenRequestHandler,
    )

    # Data Mappers
    sqla_auth_session_data_mapper = provide(source=SqlaAuthSessionDataMapper)

    # Transaction Manager
    sqla_auth_transaction_manager = provide(source=SqlaAuthTransactionManager)

    # Concrete Objects
    infra_objects = provide_all(
        AuthSessionManager,
        StrAuthSessionIdGenerator,
        UtcAuthSessionTimer,
        JwtTokenManager,
        JwtAccessTokenProcessor,
        AuthSessionIdentityProvider,
        SqlaUserDataMapper,
        SqlaUserReader,
        SqlaUserTransactionManager,
    )

    # "Interactors" (Infrastructure handlers)
    interactors = provide_all(
        SignUpHandler,
        LogInHandler,
        LogOutHandler,
    )
