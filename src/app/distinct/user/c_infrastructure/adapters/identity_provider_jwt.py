from app.common.b_application.exceptions import AdapterError, GatewayError
from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.entity_user import User
from app.distinct.user.a_domain.enums import UserRoleEnum
from app.distinct.user.a_domain.exceptions.expiration import SessionExpired
from app.distinct.user.a_domain.exceptions.non_existence import (
    SessionNotFoundById,
    UserNotFoundById,
)
from app.distinct.user.a_domain.vo_session import SessionId
from app.distinct.user.a_domain.vo_user import UserId
from app.distinct.user.b_application.gateways.session import SessionGateway
from app.distinct.user.b_application.gateways.user import UserGateway
from app.distinct.user.b_application.ports.access_token_processor import (
    AccessTokenProcessor,
)
from app.distinct.user.b_application.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)
from app.distinct.user.b_application.ports.identity_provider import IdentityProvider
from app.distinct.user.b_application.ports.session_timer import SessionTimer


class JwtIdentityProvider(IdentityProvider):
    def __init__(
        self,
        access_token_handler: AccessTokenRequestHandler,
        token_processor: AccessTokenProcessor,
        session_timer: SessionTimer,
        session_gateway: SessionGateway,
        user_gateway: UserGateway,
    ):
        self._access_token_handler = access_token_handler
        self._token_processor = token_processor
        self._session_timer = session_timer
        self._session_gateway = session_gateway
        self._user_gateway = user_gateway

    async def get_current_session(self) -> Session:
        """
        :raises AdapterError:
        :raises SessionNotFoundById:
        :raises GatewayError:
        :raises SessionExpired:
        """
        try:
            access_token: str = (
                self._access_token_handler.get_access_token_from_request()
            )
            session_id: SessionId = self._token_processor.extract_session_id(
                access_token
            )
        except AdapterError:
            raise

        try:
            session: Session = await self._session_gateway.read_by_id(session_id)
        except (SessionNotFoundById, GatewayError):
            raise

        if session.expiration.value <= self._session_timer.current_time:
            raise SessionExpired(session.id_)

        return session

    async def get_current_user_id(self) -> UserId:
        """
        :raises AdapterError:
        :raises SessionNotFoundById:
        :raises GatewayError:
        :raises SessionExpired:
        """
        try:
            session: Session = await self.get_current_session()
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
        ):
            raise

        return session.user_id

    async def get_current_user_roles(self) -> set[UserRoleEnum]:
        """
        :raises AdapterError:
        :raises SessionNotFoundById:
        :raises GatewayError:
        :raises SessionExpired:
        :raises UserNotFoundById:
        """
        try:
            user_id: UserId = await self.get_current_user_id()
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
        ):
            raise

        try:
            user: User = await self._user_gateway.read_by_id(user_id)
        except (UserNotFoundById, GatewayError):
            raise

        return user.roles
