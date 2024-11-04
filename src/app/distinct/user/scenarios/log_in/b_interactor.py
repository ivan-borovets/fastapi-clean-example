import logging

from app.base.b_application.interactors import InteractorStrict
from app.common.b_application.exceptions import GatewayError
from app.distinct.user.a_domain.exceptions.non_existence import UserNotFoundByUsername
from app.distinct.user.a_domain.vo_user import Username
from app.distinct.user.b_application.exceptions import AuthenticationError
from app.distinct.user.b_application.service_auth import AuthService
from app.distinct.user.scenarios.log_in.b_payload import LogInRequest, LogInResponse

log = logging.getLogger(__name__)


class LogInInteractor(InteractorStrict[LogInRequest, LogInResponse]):
    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    async def __call__(self, request_data: LogInRequest) -> LogInResponse:
        """
        :raises AuthenticationError:
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """
        username: Username = Username(request_data.username)
        password: str = request_data.password
        try:
            await self._auth_service.log_in(username, password)
        except (
            AuthenticationError,
            UserNotFoundByUsername,
            GatewayError,
        ):
            raise
        return LogInResponse("Successfully logged in.")
