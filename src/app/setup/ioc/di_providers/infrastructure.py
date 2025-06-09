from dishka import Provider, Scope, alias, provide, provide_all

from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.infrastructure.adapters.sqla_main_transaction_manager import (
    SqlaMainTransactionManager,
)
from app.infrastructure.adapters.user.sqla_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.user.sqla_reader import SqlaUserReader
from app.infrastructure.auth_session.adapters.identity_provider import (
    AuthSessionIdentityProvider,
)
from app.infrastructure.auth_session.adapters.sqla_data_mapper import (
    SqlaAuthSessionDataMapper,
)
from app.infrastructure.auth_session.adapters.sqla_transaction_manager import (
    SqlaAuthSessionTransactionManager,
)
from app.infrastructure.auth_session.ports.gateway import AuthSessionGateway
from app.infrastructure.auth_session.ports.transaction_manager import (
    AuthSessionTransactionManager,
)
from app.infrastructure.auth_session.ports.transport import AuthSessionTransport
from app.infrastructure.auth_session.service import AuthSessionService
from app.infrastructure.auth_session.str_id_generator import StrAuthSessionIdGenerator
from app.infrastructure.auth_session.utc_timer import UtcAuthSessionTimer
from app.infrastructure.handlers.log_in import LogInHandler
from app.infrastructure.handlers.log_out import LogOutHandler
from app.infrastructure.handlers.sign_up import SignUpHandler
from app.infrastructure.ports.user.data_gateway import UserDataGateway
from app.infrastructure.ports.user.transaction_manager import (
    UserTransactionManager,
)
from app.infrastructure.sqla_persistence.provider import (
    get_async_engine,
    get_async_session_factory,
    get_auth_async_session,
    get_main_async_session,
)
from app.presentation.web.adapters.jwt_cookie_auth_session_transport import (
    JwtCookieAuthSessionTransport,
)


class InfrastructureProvider(Provider):
    scope = Scope.REQUEST

    # Ports Persistence
    user_data_gateway = alias(
        source=UserCommandGateway,
        provides=UserDataGateway,
    )
    user_tx_manager = alias(
        source=SqlaMainTransactionManager,
        provides=UserTransactionManager,
    )

    # Auth Services
    auth_session_service = provide(source=AuthSessionService)

    # Auth Ports Persistence
    auth_session_gateway = provide(
        source=SqlaAuthSessionDataMapper,
        provides=AuthSessionGateway,
    )
    auth_session_tx_manager = provide(
        source=SqlaAuthSessionTransactionManager,
        provides=AuthSessionTransactionManager,
    )

    # Auth Ports
    auth_session_transport = provide(
        source=JwtCookieAuthSessionTransport,
        provides=AuthSessionTransport,
    )

    # "Interactors" (Infrastructure handlers)
    interactors = provide_all(
        SignUpHandler,
        LogInHandler,
        LogOutHandler,
    )

    # Concrete Objects
    infrastructure_objects = provide_all(
        StrAuthSessionIdGenerator,
        UtcAuthSessionTimer,
        AuthSessionIdentityProvider,
        SqlaAuthSessionDataMapper,
        SqlaAuthSessionTransactionManager,
        SqlaUserDataMapper,
        SqlaUserReader,
        SqlaMainTransactionManager,
    )


def infrastructure_provider() -> InfrastructureProvider:
    provider = InfrastructureProvider()

    # SQLA Persistence
    provider.provide(
        source=get_async_engine,
        scope=Scope.APP,
    )
    provider.provide(
        source=get_async_session_factory,
        scope=Scope.APP,
    )
    provider.provide(
        source=get_main_async_session,
        scope=Scope.REQUEST,
    )
    provider.provide(
        source=get_auth_async_session,
        scope=Scope.REQUEST,
    )
    return provider
