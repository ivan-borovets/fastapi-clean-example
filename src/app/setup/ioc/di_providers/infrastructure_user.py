# pylint: disable=C0301 (line-too-long)

from dishka import Provider, Scope, provide

from app.application.user.data_gateways.session import SessionDataGateway
from app.application.user.data_gateways.user import UserDataGateway
from app.application.user.ports.access_token_processor import AccessTokenProcessor
from app.application.user.ports.identity_provider import IdentityProvider
from app.application.user.ports.password_hasher import PasswordHasher
from app.application.user.ports.session_id_generator import SessionIdGenerator
from app.application.user.ports.session_timer import SessionTimer
from app.application.user.ports.user_id_generator import UserIdGenerator
from app.infrastructure.user.adapters.access_token_processor_jwt import (
    JwtAccessTokenProcessor,
)
from app.infrastructure.user.adapters.identity_provider_jwt import JwtIdentityProvider
from app.infrastructure.user.adapters.password_hasher_bcrypt import BcryptPasswordHasher
from app.infrastructure.user.adapters.session_id_generator_str import (
    StrSessionIdGenerator,
)
from app.infrastructure.user.adapters.session_timer_utc import UtcSessionTimer
from app.infrastructure.user.adapters.user_id_generator_uuid import UuidUserIdGenerator
from app.infrastructure.user.data_gateways_sqla.session import SqlaSessionDataGateway
from app.infrastructure.user.data_gateways_sqla.user import SqlaUserDataGateway


class UserDataGatewaysProvider(Provider):
    session_data_gateway = provide(
        source=SqlaSessionDataGateway,
        scope=Scope.REQUEST,
        provides=SessionDataGateway,
    )
    user_data_gateway = provide(
        source=SqlaUserDataGateway,
        scope=Scope.REQUEST,
        provides=UserDataGateway,
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
