import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import Username
from app.domain.exceptions.user.non_existence import UserNotFoundByUsername
from app.domain.services.user import UserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RevokeAdminRequest:
    username: str


class RevokeAdminResponse(TypedDict):
    username: str
    status: ResponseStatusEnum


class RevokeAdminInteractor:
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

    async def __call__(self, request_data: RevokeAdminRequest) -> RevokeAdminResponse:
        log.info(
            "Revoke admin by admin: started. Username: '%s'.", request_data.username
        )

        await self._authorization_service.authorize_action_by_role(
            UserRoleEnum.SUPER_ADMIN
        )

        username = Username(request_data.username)

        user: User | None = await self._user_command_gateway.read_by_username(
            username, for_update=True
        )
        if user is None:
            raise UserNotFoundByUsername(username)

        self._user_service.toggle_user_admin_role(user, False)
        await self._transaction_manager.commit()

        log.info(
            "Revoke admin by admin: finished. Username: '%s'.", user.username.value
        )
        return RevokeAdminResponse(
            username=user.username.value,
            status=ResponseStatusEnum.UPDATED,
        )
