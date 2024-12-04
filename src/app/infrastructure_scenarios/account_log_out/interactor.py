import logging

from app.application.base.interactors import InteractorFlexible
from app.application.exceptions import DataGatewayError
from app.application.user.exceptions import AuthenticationError
from app.domain.user.entity import User
from app.domain.user.value_objects import UserId
from app.infrastructure.adapters_application.identity_provider_session import (
    SessionIdentityProvider,
)
from app.infrastructure.adapters_application.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)
from app.infrastructure.record_session import SessionRecord
from app.infrastructure.session.exceptions import AdapterError, SessionNotFoundById
from app.infrastructure.session.services.jwt_token import JwtTokenService
from app.infrastructure.session.services.session import SessionService
from app.infrastructure_scenarios.account_log_out.payload import LogOutResponse

log = logging.getLogger(__name__)


class LogOutInteractor(InteractorFlexible):
    """
    :raises AuthenticationError:
    :raises DataGatewayError:
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

        try:
            current_session: SessionRecord = (
                await self._session_service.get_current_session()
            )
        except (AdapterError, DataGatewayError, SessionNotFoundById) as error:
            log.error("Session retrieving failed: '%s'", error)
            raise AuthenticationError("Not authenticated.") from error

        self._jwt_token_service.delete_access_token_from_request()
        log.debug("Access token deleted. Session id: '%s'.", current_session.id_)

        try:
            await self._session_service.delete_session(current_session.id_)
        except (DataGatewayError, SessionNotFoundById) as error:
            log.error("Session deletion failed: '%s'", error)
            raise DataGatewayError("Session deletion failed.") from error

        log.info("Log out: done. Username: '%s'.", user.username.value)
        return LogOutResponse("Logged out: successful.")
