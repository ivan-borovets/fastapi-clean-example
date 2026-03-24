import logging
from dataclasses import dataclass
from typing import Final

from app.core.common.authorization.current_user_service import CurrentUserService
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from app.infrastructure.auth_ctx.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.auth_ctx.service import AuthService
from app.infrastructure.auth_ctx.sqla_user_tx_storage import AuthSqlaUserTxStorage

AUTH_ACCOUNT_INACTIVE: Final[str] = "Your account is inactive. Please contact support."

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInRequest:
    username: str
    password: str


class LogIn:
    """
    - Open to everyone.
    - Authenticates registered user, sets JWT with session ID in cookies, and creates session.
    - Logged-in user cannot log in again until session expires or is terminated.
    - Authentication renews automatically when accessing protected routes before expiration.
    - If JWT is invalid, expired, or session is terminated, user loses authentication.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_tx_storage: AuthSqlaUserTxStorage,
        user_service: UserService,
        auth_service: AuthService,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_tx_storage = user_tx_storage
        self._user_service = user_service
        self._auth_service = auth_service

    async def execute(self, request: LogInRequest) -> None:
        logger.info("Log in: started.")

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError
        except AuthenticationError:
            pass

        username = Username(request.username)
        password = RawPassword(request.password)
        user = await self._user_tx_storage.get_by_username(username)
        if user is None:
            raise AuthenticationError

        if not await self._user_service.is_password_valid(user, password):
            raise AuthenticationError

        if not user.is_active:
            raise AuthenticationError(AUTH_ACCOUNT_INACTIVE)

        await self._auth_service.issue_session(user.id_)

        logger.info("Log in: done.")
