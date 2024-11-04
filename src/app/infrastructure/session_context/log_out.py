# pylint: disable=C0301 (line-too-long)
import logging
from dataclasses import dataclass

from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import UserId
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.session_context.common.application_adapters.session_identity_provider import (
    SessionIdentityProvider,
)
from app.infrastructure.session_context.common.authentication_exceptions import (
    AuthenticationError,
)
from app.infrastructure.session_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.session_context.common.managers.session import SessionManager
from app.infrastructure.session_context.common.session_record import SessionRecord

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LogOutResponse:
    message: str


class LogOutInteractor:
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    """

    def __init__(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        session_manager: SessionManager,
        jtw_token_manager: JwtTokenManager,
    ):
        self._session_identity_provider = session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._session_manager = session_manager
        self._jwt_token_manager = jtw_token_manager

    async def __call__(self) -> LogOutResponse:
        log.info("Log out: started for unknown user.")

        user_id: UserId = await self._session_identity_provider.get_current_user_id()

        user: User | None = await self._sqla_user_data_mapper.read_by_id(user_id)
        if user is None:
            raise AuthenticationError("Not authenticated.")

        log.info("Log out: user identified. Username: '%s'.", user.username.value)

        current_session: SessionRecord | None = (
            await self._session_manager.get_current_session()
        )
        if current_session is None:
            raise AuthenticationError("Not authenticated.")

        self._jwt_token_manager.delete_access_token_from_request()
        log.debug("Access token deleted. Session id: '%s'.", current_session.id_)

        if not await self._session_manager.delete_session(current_session.id_):
            log.debug(
                (
                    "Log out: failed. "
                    "Session wasn't deleted. "
                    "Username: '%s'. "
                    "Session id: '%s'."
                ),
                user.username.value,
                current_session.id_,
            )
            return LogOutResponse("Logged out: incomplete.")

        log.info("Log out: done. Username: '%s'.", user.username.value)
        return LogOutResponse("Logged out: successful.")
