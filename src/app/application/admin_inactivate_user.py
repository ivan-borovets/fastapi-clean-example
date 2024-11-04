import logging
from dataclasses import dataclass

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.committer import Committer
from app.application.common.ports.user_data_gateway import UserDataGateway
from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import Username
from app.domain.exceptions.user.non_existence import UserNotFoundByUsername
from app.domain.services.user import UserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class InactivateUserRequest:
    username: str


@dataclass(frozen=True, slots=True)
class InactivateUserResponse:
    username: str
    status: ResponseStatusEnum


class InactivateUserInteractor:
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
        access_revoker: AccessRevoker,
    ):
        self._authorization_service = authorization_service
        self._user_data_gateway = user_data_gateway
        self._user_service = user_service
        self._committer = committer
        self._access_revoker = access_revoker

    async def __call__(
        self, request_data: InactivateUserRequest
    ) -> InactivateUserResponse:
        log.info(
            "Inactivate user by admin: started. Username: '%s'.", request_data.username
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

        self._user_service.toggle_user_activation(user, False)
        await self._committer.commit()

        await self._access_revoker.remove_all_user_access(user.id_)

        log.info(
            "Inactivate user by admin: finished. Username: '%s'.", user.username.value
        )
        return InactivateUserResponse(user.username.value, ResponseStatusEnum.UPDATED)
