import logging

from app.application.user.ports.identity_provider import IdentityProvider
from app.domain.user.value_objects import UserId
from app.infrastructure.record_session import SessionRecord
from app.infrastructure.session.exceptions import AuthenticationError
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

        access_token: str | None = (
            self._jwt_token_service.get_access_token_from_request()
        )
        if access_token is None:
            raise AuthenticationError("Not authenticated.")

        session_id: str | None = (
            self._jwt_token_service.get_session_id_from_access_token(access_token)
        )
        if session_id is None:
            raise AuthenticationError("Not authenticated.")

        session: SessionRecord | None = await self._session_service.get_session(
            session_id, for_update=True
        )
        if session is None:
            raise AuthenticationError("Not authenticated.")

        if self._session_service.is_session_expired(session):
            raise AuthenticationError("Not authenticated.")

        if self._session_service.is_session_near_expiry(session):
            await self._session_service.prolong_session(session)

            new_access_token: str = self._jwt_token_service.issue_access_token(
                session.id_
            )
            self._jwt_token_service.add_access_token_to_request(new_access_token)

        log.debug("Get current user id: done.")
        return session.user_id
