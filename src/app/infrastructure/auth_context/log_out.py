import logging

from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import UserId
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
from app.infrastructure.auth_context.common.sqla_auth_transaction_manager import (
    SqlaAuthTransactionManager,
)

log = logging.getLogger(__name__)


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
        jwt_token_manager: JwtTokenManager,
        sqla_auth_transaction_manager: SqlaAuthTransactionManager,
    ):
        self._auth_session_identity_provider = auth_session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._auth_session_manager = auth_session_manager
        self._jwt_token_manager = jwt_token_manager
        self._sqla_auth_transaction_manager = sqla_auth_transaction_manager

    async def __call__(self) -> None:
        log.info("Log out: started for unknown user.")

        user_id: UserId = (
            await self._auth_session_identity_provider.get_current_user_id()
        )

        user: User | None = await self._sqla_user_data_mapper.read_by_id(user_id)
        if user is None:
            raise AuthenticationError("Not authenticated.")

        log.info("Log out: user identified. Username: '%s'.", user.username.value)

        current_auth_session: (
            AuthSession | None
        ) = await self._auth_session_manager.get_current_auth_session()
        if current_auth_session is None:
            raise AuthenticationError("Not authenticated.")

        self._jwt_token_manager.delete_access_token_from_request()
        log.debug(
            "Access token deleted. Auth session id: '%s'.",
            current_auth_session.id_,
        )

        if not await self._auth_session_manager.delete_auth_session(
            current_auth_session.id_,
        ):
            log.warning(
                (
                    "Log out failed: partially completed. "
                    "Access token was deleted, but auth session was not. "
                    "Username: '%s'. Auth session ID: '%s'."
                ),
                user.username.value,
                current_auth_session.id_,
            )

        await self._sqla_auth_transaction_manager.commit()

        log.info("Log out: done. Username: '%s'.", user.username.value)
