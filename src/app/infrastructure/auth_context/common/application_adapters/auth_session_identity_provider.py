import logging

from app.application.common.ports.identity_provider import IdentityProvider
from app.domain.entities.user.value_objects import UserId
from app.infrastructure.adapters.application.sqla_transaction_manager import (
    SqlaTransactionManager,
)
from app.infrastructure.auth_context.common.auth_exceptions import AuthenticationError
from app.infrastructure.auth_context.common.auth_session import AuthSession
from app.infrastructure.auth_context.common.managers.auth_session import (
    AuthSessionManager,
)
from app.infrastructure.auth_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.exceptions.gateway_implementations import DataMapperError

log = logging.getLogger(__name__)


class AuthSessionIdentityProvider(IdentityProvider):
    def __init__(
        self,
        jwt_token_manager: JwtTokenManager,
        auth_session_manager: AuthSessionManager,
        sqla_transaction_manager: SqlaTransactionManager,
    ):
        self._jwt_token_manager = jwt_token_manager
        self._auth_session_manager = auth_session_manager
        self._sqla_transaction_manager = sqla_transaction_manager

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

        auth_session_id: str | None = (
            self._jwt_token_manager.get_auth_session_id_from_access_token(access_token)
        )
        if auth_session_id is None:
            raise AuthenticationError("Not authenticated.")

        auth_session: AuthSession | None = (
            await self._auth_session_manager.get_auth_session(
                auth_session_id, for_update=True
            )
        )
        if auth_session is None:
            raise AuthenticationError("Not authenticated.")

        if self._auth_session_manager.is_auth_session_expired(auth_session):
            raise AuthenticationError("Not authenticated.")

        if self._auth_session_manager.is_auth_session_near_expiry(auth_session):
            await self._auth_session_manager.prolong_auth_session(auth_session)

            new_access_token: str = self._jwt_token_manager.issue_access_token(
                auth_session.id_
            )
            self._jwt_token_manager.add_access_token_to_request(new_access_token)

            try:
                await self._sqla_transaction_manager.commit()

            except DataMapperError as error:
                log.error("Auto prolongation of auth session failed: '%s'", error)

        log.debug("Get current user id: done.")
        return auth_session.user_id
