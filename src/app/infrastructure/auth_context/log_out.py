# pylint: disable=C0301 (line-too-long)
import logging
from typing import TypedDict

from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import UserId
from app.infrastructure.adapters.application.sqla_transaction_manager import (
    SqlaTransactionManager,
)
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.auth_context.common.application_adapters.auth_session_identity_provider import (
    AuthSessionIdentityProvider,
)
from app.infrastructure.auth_context.common.auth_exceptions import AuthenticationError
from app.infrastructure.auth_context.common.auth_session import AuthSession
from app.infrastructure.auth_context.common.managers.auth_session import (
    AuthSessionManager,
)
from app.infrastructure.auth_context.common.managers.jwt_token import JwtTokenManager

log = logging.getLogger(__name__)


class LogOutResponse(TypedDict):
    message: str


class LogOutHandler:
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    """

    def __init__(
        self,
        auth_session_identity_provider: AuthSessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        auth_session_manager: AuthSessionManager,
        jtw_token_manager: JwtTokenManager,
        sqla_transaction_manager: SqlaTransactionManager,
    ):
        self._auth_session_identity_provider = auth_session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._auth_session_manager = auth_session_manager
        self._jwt_token_manager = jtw_token_manager
        self._sqla_transaction_manager = sqla_transaction_manager

    async def __call__(self) -> LogOutResponse:
        log.info("Log out: started for unknown user.")

        user_id: UserId = (
            await self._auth_session_identity_provider.get_current_user_id()
        )

        user: User | None = await self._sqla_user_data_mapper.read_by_id(user_id)
        if user is None:
            raise AuthenticationError("Not authenticated.")

        log.info("Log out: user identified. Username: '%s'.", user.username.value)

        current_auth_session: AuthSession | None = (
            await self._auth_session_manager.get_current_auth_session()
        )
        if current_auth_session is None:
            raise AuthenticationError("Not authenticated.")

        self._jwt_token_manager.delete_access_token_from_request()
        log.debug(
            "Access token deleted. Auth session id: '%s'.", current_auth_session.id_
        )

        if not await self._auth_session_manager.delete_auth_session(
            current_auth_session.id_
        ):
            log.debug(
                (
                    "Log out: failed. "
                    "Auth session wasn't deleted. "
                    "Username: '%s'. "
                    "Auth session id: '%s'."
                ),
                user.username.value,
                current_auth_session.id_,
            )
            return LogOutResponse(message="Logged out: incomplete.")

        await self._sqla_transaction_manager.commit()

        log.info("Log out: done. Username: '%s'.", user.username.value)
        return LogOutResponse(message="Logged out: successful.")
