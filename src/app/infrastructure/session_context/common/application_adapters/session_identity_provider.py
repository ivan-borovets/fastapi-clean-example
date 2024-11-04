import logging

from app.application.common.ports.identity_provider import IdentityProvider
from app.domain.user.value_objects import UserId
from app.infrastructure.session_context.common.authentication_exceptions import (
    AuthenticationError,
)
from app.infrastructure.session_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.session_context.common.managers.session import SessionManager
from app.infrastructure.session_context.common.session_record import SessionRecord

log = logging.getLogger(__name__)


class SessionIdentityProvider(IdentityProvider):
    def __init__(
        self,
        jwt_token_manager: JwtTokenManager,
        session_manager: SessionManager,
    ):
        self._jwt_token_manager = jwt_token_manager
        self._session_manager = session_manager

    async def get_current_user_id(self) -> UserId:
        """
        :raises AuthenticationError:
        """
        log.debug("Get current user id: started.")

        access_token: str | None = (
            self._jwt_token_manager.get_access_token_from_request()
        )
        if access_token is None:
            raise AuthenticationError("Not authenticated.")

        session_id: str | None = (
            self._jwt_token_manager.get_session_id_from_access_token(access_token)
        )
        if session_id is None:
            raise AuthenticationError("Not authenticated.")

        session: SessionRecord | None = await self._session_manager.get_session(
            session_id, for_update=True
        )
        if session is None:
            raise AuthenticationError("Not authenticated.")

        if self._session_manager.is_session_expired(session):
            raise AuthenticationError("Not authenticated.")

        if self._session_manager.is_session_near_expiry(session):
            await self._session_manager.prolong_session(session)

            new_access_token: str = self._jwt_token_manager.issue_access_token(
                session.id_
            )
            self._jwt_token_manager.add_access_token_to_request(new_access_token)

        log.debug("Get current user id: done.")
        return session.user_id
