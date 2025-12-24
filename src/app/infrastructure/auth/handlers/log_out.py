import logging

from app.application.common.services.current_user import CurrentUserService
from app.infrastructure.auth.session.service import AuthSessionService

log = logging.getLogger(__name__)


class LogOutHandler:
    """
    - Open to authenticated users.
    - Logs the user out by deleting the JWT access token from cookies
    and removing the session from the database.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        auth_session_service: AuthSessionService,
    ) -> None:
        self._current_user_service = current_user_service
        self._auth_session_service = auth_session_service

    async def execute(self) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        log.info("Log out: started for unknown user.")

        current_user = await self._current_user_service.get_current_user()

        log.info("Log out: user identified. User ID: '%s'.", current_user.id_)

        await self._auth_session_service.terminate_current_session()

        log.info("Log out: done. User ID: '%s'.", current_user.id_)
