import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import Username
from app.domain.exceptions.user.non_existence import UserNotFoundByUsername
from app.domain.services.user import UserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ReactivateUserRequest:
    username: str


class ReactivateUserResponse(TypedDict):
    username: str
    status: ResponseStatusEnum


class ReactivateUserInteractor:
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
    :raises DomainFieldError:
    :raises UserNotFoundByUsername:
    """

    def __init__(
        self,
        authorization_service: AuthorizationService,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ):
        self._authorization_service = authorization_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def __call__(
        self, request_data: ReactivateUserRequest
    ) -> ReactivateUserResponse:
        log.info(
            "Reactivate user by admin: started. Username: '%s'.", request_data.username
        )

        await self._authorization_service.authorize_action(PermissionEnum.MANAGE_USERS)

        username = Username(request_data.username)

        user: User | None = await self._user_command_gateway.read_by_username(
            username, for_update=True
        )
        if user is None:
            raise UserNotFoundByUsername(username)

        await self._authorization_service.authorize_action_by_role(
            user.role, for_subordinate_only=True
        )

        self._user_service.toggle_user_activation(user, True)
        await self._transaction_manager.commit()

        log.info(
            "Reactivate user by admin: finished. Username: '%s'.", user.username.value
        )
        return ReactivateUserResponse(
            username=user.username.value,
            status=ResponseStatusEnum.UPDATED,
        )
