import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user import User
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.domain.value_objects.username.username import Username
from app.infrastructure.constants import AUTH_ALREADY_AUTHENTICATED
from app.infrastructure.exceptions.authentication import (
    AlreadyAuthenticatedError,
    AuthenticationError,
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
    Open to everyone.
    Registers a new user with validation and uniqueness checks.
    Passwords are peppered, salted, and stored as hashes.
    A logged-in user cannot sign up until the session expires or is terminated.

    :raises AlreadyAuthenticatedError:
    :raises AuthorizationError:
    :raises DataMapperError:
    :raises DomainFieldError:
    :raises RoleAssignmentNotPermittedError:
    :raises UsernameAlreadyExists:
    """

    def __init__(
        self,
        user_command_gateway: UserCommandGateway,
        transaction_manager: TransactionManager,
        current_user_service: CurrentUserService,
        user_service: UserService,
    ):
        self._user_command_gateway = user_command_gateway
        self._transaction_manager = transaction_manager
        self._current_user_service = current_user_service
        self._user_service = user_service

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        log.info("Sign up: started. Username: '%s'.", request_data.username)

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)

        user: User = self._user_service.create_user(username, password)

        self._user_command_gateway.add(user)

        try:
            await self._transaction_manager.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("Sign up: done. Username: '%s'.", user.username.value)
        return SignUpResponse(id=user.id_.value)
