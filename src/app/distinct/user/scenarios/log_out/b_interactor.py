import logging

from app.base.b_application.interactors import InteractorFlexible
from app.distinct.user.b_application.exceptions import AuthenticationError
from app.distinct.user.b_application.service_auth import AuthService
from app.distinct.user.scenarios.log_out.b_payload import LogOutResponse

log = logging.getLogger(__name__)


class LogOutInteractor(InteractorFlexible):
    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    async def __call__(self) -> LogOutResponse:
        """
        :raises AuthenticationError:
        """
        try:
            await self._auth_service.log_out()
        except AuthenticationError:
            raise

        return LogOutResponse("Successfully logged out.")
