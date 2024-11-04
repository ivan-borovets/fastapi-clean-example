import logging
from dataclasses import dataclass

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.committer import Committer
from app.application.common.ports.user_data_gateway import UserDataGateway
from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.user.entity import User
from app.domain.user.exceptions.non_existence import UserNotFoundByUsername
from app.domain.user.service import UserService
from app.domain.user.value_objects import Username

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ReactivateUserRequest:
    username: str


@dataclass(frozen=True, slots=True)
class ReactivateUserResponse:
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
        user_data_gateway: UserDataGateway,
        user_service: UserService,
        committer: Committer,
    ):
        self._authorization_service = authorization_service
        self._user_data_gateway = user_data_gateway
        self._user_service = user_service
        self._committer = committer

    async def __call__(
        self, request_data: ReactivateUserRequest
    ) -> ReactivateUserResponse:
        log.info(
            "Reactivate user by admin: started. Username: '%s'.", request_data.username
        )

        await self._authorization_service.authorize_action(PermissionEnum.MANAGE_USERS)

        username: Username = Username(request_data.username)

        user: User | None = await self._user_data_gateway.read_by_username(
            username, for_update=True
        )
        if user is None:
            raise UserNotFoundByUsername(username)

        await self._authorization_service.authorize_action_by_role(
            user.role, for_subordinate_only=True
        )

        self._user_service.toggle_user_activation(user, True)
        await self._committer.commit()

        log.info(
            "Reactivate user by admin: finished. Username: '%s'.", user.username.value
        )
        return ReactivateUserResponse(user.username.value, ResponseStatusEnum.UPDATED)
