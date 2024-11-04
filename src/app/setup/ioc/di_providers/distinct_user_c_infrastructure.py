# pylint: disable=C0301 (line-too-long)

from dishka import Provider, Scope, provide

from app.distinct.user.b_application.gateways.session import SessionGateway
from app.distinct.user.b_application.gateways.user import UserGateway
from app.distinct.user.b_application.ports.access_token_processor import (
    AccessTokenProcessor,
)
from app.distinct.user.b_application.ports.identity_provider import IdentityProvider
from app.distinct.user.b_application.ports.password_hasher import PasswordHasher
from app.distinct.user.b_application.ports.session_id_generator import (
    SessionIdGenerator,
)
from app.distinct.user.b_application.ports.session_timer import SessionTimer
from app.distinct.user.b_application.ports.user_id_generator import UserIdGenerator
from app.distinct.user.c_infrastructure.adapters.access_token_processor_jwt import (
    JwtAccessTokenProcessor,
)
from app.distinct.user.c_infrastructure.adapters.identity_provider_jwt import (
    JwtIdentityProvider,
)
from app.distinct.user.c_infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)
from app.distinct.user.c_infrastructure.adapters.session_id_generator_str import (
    StrSessionIdGenerator,
)
from app.distinct.user.c_infrastructure.adapters.session_timer_utc import (
    UtcSessionTimer,
)
from app.distinct.user.c_infrastructure.adapters.user_id_generator_uuid import (
    UuidUserIdGenerator,
)
from app.distinct.user.c_infrastructure.gateways_impl_sqla.session import (
    SqlaSessionGateway,
)
from app.distinct.user.c_infrastructure.gateways_impl_sqla.user import SqlaUserGateway


class UserGatewaysProvider(Provider):
    session_gateway = provide(
        source=SqlaSessionGateway,
        scope=Scope.REQUEST,
        provides=SessionGateway,
    )

    user_gateway = provide(
        source=SqlaUserGateway,
        scope=Scope.REQUEST,
        provides=UserGateway,
    )


class UserAdaptersProvider(Provider):
    access_token_processor = provide(
        source=JwtAccessTokenProcessor,
        scope=Scope.REQUEST,
        provides=AccessTokenProcessor,
    )
    identity_provider = provide(
        source=JwtIdentityProvider,
        scope=Scope.REQUEST,
        provides=IdentityProvider,
    )
    password_hasher = provide(
        source=BcryptPasswordHasher,
        scope=Scope.APP,
        provides=PasswordHasher,
    )
    session_id_generator = provide(
        source=StrSessionIdGenerator,
        scope=Scope.APP,
        provides=SessionIdGenerator,
    )
    session_timer = provide(
        source=UtcSessionTimer,
        scope=Scope.APP,
        provides=SessionTimer,
    )
    user_id_generator = provide(
        source=UuidUserIdGenerator,
        scope=Scope.APP,
        provides=UserIdGenerator,
    )
