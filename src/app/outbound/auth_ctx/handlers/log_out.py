import logging

from app.core.common.authorization.current_user_service import CurrentUserService
from app.outbound.auth_ctx.service import AuthService

logger = logging.getLogger(__name__)


class LogOut:
    """
    - Open to authenticated users.
    - Logs user out by deleting JWT from cookies and removing session from database.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        auth_service: AuthService,
    ) -> None:
        self._current_user_service = current_user_service
        self._auth_service = auth_service

    async def execute(self) -> None:
        logger.info("Log out: started.")

        await self._current_user_service.get_current_user()
        await self._auth_service.logout_current_session()

        logger.info("Log out: done.")
