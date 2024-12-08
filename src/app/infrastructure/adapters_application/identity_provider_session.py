import logging

from app.application.exceptions import DataGatewayError
from app.application.user_helpers.exceptions import AuthenticationError
from app.application.user_helpers.ports.identity_provider import IdentityProvider
from app.domain.user.value_objects import UserId
from app.infrastructure.record_session import SessionRecord
from app.infrastructure.session.exceptions import (
    AdapterError,
    SessionExpired,
    SessionNotFoundById,
)
from app.infrastructure.session.services.jwt_token import JwtTokenService
from app.infrastructure.session.services.session import SessionService

log = logging.getLogger(__name__)


class SessionIdentityProvider(IdentityProvider):
    def __init__(
        self,
        jwt_token_service: JwtTokenService,
        session_service: SessionService,
    ):
        self._jwt_token_service = jwt_token_service
        self._session_service = session_service

    async def get_current_user_id(self) -> UserId:
        """
        :raises AuthenticationError:
        """
        log.debug("Get current user id: started.")

        try:
            access_token: str = self._jwt_token_service.get_access_token_from_request()
            session_id: str = self._jwt_token_service.get_session_id_from_access_token(
                access_token
            )
        except AdapterError as error:
            raise AuthenticationError("Not authenticated") from error

        try:
            session: SessionRecord = await self._session_service.get_session(
                session_id, for_update=True
            )
        except (DataGatewayError, SessionNotFoundById) as error:
            raise AuthenticationError("Not authenticated") from error

        try:
            self._session_service.check_session_expiration(session)
        except SessionExpired as error:
            raise AuthenticationError("Not authenticated") from error

        if self._session_service.is_session_near_expiry(session):
            await self._session_service.prolong_session(session)

        log.debug("Get current user id: done.")
        return session.user_id
