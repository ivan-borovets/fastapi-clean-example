import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.domain.value_objects.username.username import Username

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    password: str
    role: UserRole


class CreateUserResponse(TypedDict):
    id: UUID


class CreateUserInteractor:
    """
    Open to admins.
    Creates a new user, including admins, if the username is unique.
    Only super admins can create new admins.

    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
    :raises DomainFieldError:
    :raises UsernameAlreadyExists:
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        authorization_service: AuthorizationService,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._authorization_service = authorization_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def __call__(self, request_data: CreateUserRequest) -> CreateUserResponse:
        log.info(
            "Create user: started. Username: '%s'.",
            request_data.username,
        )

        current_user = await self._current_user_service.get_current_user()
        self._authorization_service.authorize_for_subordinate_role(
            current_user.role,
            target_role=request_data.role,
        )

        username = Username(request_data.username)
        password = RawPassword(request_data.password)
        user = self._user_service.create_user(username, password)
        user.role = request_data.role
        self._user_command_gateway.add(user)

        try:
            await self._transaction_manager.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("Create user: done. Username: '%s'.", user.username.value)
        return CreateUserResponse(id=user.id_.value)
