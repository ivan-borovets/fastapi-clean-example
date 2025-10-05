import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.current_user import CurrentUserService
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.username import Username
from app.infrastructure.auth.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.auth.handlers.constants import (
    AUTH_ALREADY_AUTHENTICATED,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpRequest:
    username: str
    password: str


class SignUpResponse(TypedDict):
    id: UUID


class SignUpHandler:
    """
    - Open to everyone.
    - Registers a new user with validation and uniqueness checks.
    - Passwords are peppered, salted, and stored as hashes.
    - A logged-in user cannot sign up until the session expires or is terminated.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_command_gateway: UserCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._user_command_gateway = user_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: SignUpRequest) -> SignUpResponse:
        """
        :raises AlreadyAuthenticatedError:
        :raises AuthorizationError:
        :raises DataMapperError:
        :raises DomainTypeError:
        :raises PasswordHasherBusyError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info("Sign up: started. Username: '%s'.", request_data.username)

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)

        user = await self._user_service.create_user(username, password)

        self._user_command_gateway.add(user)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("Sign up: done. Username: '%s'.", user.username.value)
        return SignUpResponse(id=user.id_.value)
