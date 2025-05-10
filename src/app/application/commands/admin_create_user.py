import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.response_status_enum import ResponseStatusEnum
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import RawPassword, Username
from app.domain.exceptions.user import UsernameAlreadyExists
from app.domain.services.user import UserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    password: str
    role: UserRoleEnum


class CreateUserResponse(TypedDict):
    username: str
    status: ResponseStatusEnum


class CreateUserInteractor:
    """
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
            "Create user by admin: started. Username: '%s'.", request_data.username
        )

        current_user = await self._current_user_service.get_current_user()
        self._authorization_service.authorize_for_subordinate_role(
            current_user, target_role=request_data.role
        )

        username = Username(request_data.username)
        password = RawPassword(request_data.password)
        user = self._user_service.create_user(username, password)
        user.role = request_data.role
        await self._user_command_gateway.add(user)

        try:
            await self._transaction_manager.flush()
        except UsernameAlreadyExists:
            raise

        await self._transaction_manager.commit()

        log.info("Create user by admin: finished. Username: '%s'.", user.username.value)
        return CreateUserResponse(
            username=user.username.value,
            status=ResponseStatusEnum.CREATED,
        )
