import logging

from app.application.base.interactors import InteractorFlexible
from app.domain.user.entity import User
from app.domain.user.value_objects import UserId
from app.infrastructure.record_session import SessionRecord
from app.infrastructure.session.adapters_application.identity_provider_session import (
    SessionIdentityProvider,
)
from app.infrastructure.session.exceptions import AuthenticationError
from app.infrastructure.session.scenarios.log_out.payload import LogOutResponse
from app.infrastructure.session.services.jwt_token import JwtTokenService
from app.infrastructure.session.services.session import SessionService
from app.infrastructure.user.adapters_application.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)

log = logging.getLogger(__name__)


class LogOutInteractor(InteractorFlexible):
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    """

    def __init__(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        session_service: SessionService,
        jtw_token_service: JwtTokenService,
    ):
        self._session_identity_provider = session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._session_service = session_service
        self._jwt_token_service = jtw_token_service

    async def __call__(self) -> LogOutResponse:
        log.info("Log out: started for unknown user.")

        user_id: UserId = await self._session_identity_provider.get_current_user_id()

        user: User | None = await self._sqla_user_data_mapper.read_by_id(user_id)
        if user is None:
            raise AuthenticationError("Not authenticated.")

        log.info("Log out: user identified. Username: '%s'.", user.username.value)

        current_session: SessionRecord | None = (
            await self._session_service.get_current_session()
        )
        if current_session is None:
            raise AuthenticationError("Not authenticated.")

        self._jwt_token_service.delete_access_token_from_request()
        log.debug("Access token deleted. Session id: '%s'.", current_session.id_)

        if not await self._session_service.delete_session(current_session.id_):
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
