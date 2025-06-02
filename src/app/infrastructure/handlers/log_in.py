import logging
from dataclasses import dataclass

from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user import User
from app.domain.exceptions.user import UserNotFoundByUsernameError
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.domain.value_objects.username.username import Username
from app.infrastructure.auth_session.service import AuthSessionService
from app.infrastructure.constants import (
    AUTH_ACCOUNT_INACTIVE,
    AUTH_ALREADY_AUTHENTICATED,
    AUTH_INVALID_PASSWORD,
)
from app.infrastructure.exceptions.authentication import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.ports.user.data_gateway import UserDataGateway

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInRequest:
    username: str
    password: str


class LogInHandler:
    """
    Open to everyone.
    Authenticates registered user,
    sets a JWT access token with a session ID in cookies,
    and creates a session.
    A logged-in user cannot log in again
    until the session expires or is terminated.
    Authentication renews automatically
    when accessing protected routes before expiration.
    If the JWT is invalid, expired, or the session is terminated,
    the user loses authentication.

    :raises AlreadyAuthenticatedError:
    :raises AuthorizationError:
    :raises DataMapperError:
    :raises DomainFieldError:
    :raises UserNotFoundByUsername:
    """

    def __init__(
        self,
        # abstract
        user_data_gateway: UserDataGateway,
        # concrete
        current_user_service: CurrentUserService,
        user_service: UserService,
        auth_session_service: AuthSessionService,
    ):
        self._user_data_gateway = user_data_gateway
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._auth_session_service = auth_session_service

    async def __call__(self, request_data: LogInRequest) -> None:
        log.info("Log in: started. Username: '%s'.", request_data.username)

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)

        user: User | None = await self._user_data_gateway.read_by_username(username)
        if user is None:
            raise UserNotFoundByUsernameError(username)

        if not self._user_service.is_password_valid(user, password):
            raise AuthenticationError(AUTH_INVALID_PASSWORD)

        if not user.is_active:
            raise AuthenticationError(AUTH_ACCOUNT_INACTIVE)

        await self._auth_session_service.create_session(user.id_)

        log.info(
            "Log in: done. User, ID: '%s', username '%s', role '%s'.",
            user.id_.value,
            user.username.value,
            user.role.value,
        )
