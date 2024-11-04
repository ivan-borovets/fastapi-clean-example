import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import RawPassword, Username
from app.domain.exceptions.user.non_existence import UserNotFoundByUsername
from app.domain.services.user import UserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangePasswordRequest:
    username: str
    password: str


class ChangePasswordResponse(TypedDict):
    username: str
    status: ResponseStatusEnum


class ChangePasswordInteractor:
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
        self, request_data: ChangePasswordRequest
    ) -> ChangePasswordResponse:
        log.info("Change password: started.")

        await self._authorization_service.authorize_action(PermissionEnum.EDIT_SELF)

        username: Username = Username(request_data.username)
        password: RawPassword = RawPassword(request_data.password)

        user: User | None = await self._user_command_gateway.read_by_username(
            username, for_update=True
        )
        if user is None:
            raise UserNotFoundByUsername(username)

        await self._authorization_service.authorize_action_by_user(
            user, for_subordinate_only=True
        )

        self._user_service.change_password(user, password)
        await self._transaction_manager.commit()

        log.info("Change password: finished.")
        return ChangePasswordResponse(
            username=user.username.value,
            status=ResponseStatusEnum.UPDATED,
        )
