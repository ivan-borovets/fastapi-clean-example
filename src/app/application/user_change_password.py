import logging
from dataclasses import dataclass

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.committer import Committer
from app.application.common.ports.user_data_gateway import UserDataGateway
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


@dataclass(frozen=True, slots=True)
class ChangePasswordResponse:
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
        user_data_gateway: UserDataGateway,
        user_service: UserService,
        committer: Committer,
    ):
        self._authorization_service = authorization_service
        self._user_data_gateway = user_data_gateway
        self._user_service = user_service
        self._committer = committer

    async def __call__(
        self, request_data: ChangePasswordRequest
    ) -> ChangePasswordResponse:
        log.info("Change password: started.")

        await self._authorization_service.authorize_action(PermissionEnum.EDIT_SELF)

        username: Username = Username(request_data.username)
        password: RawPassword = RawPassword(request_data.password)

        user: User | None = await self._user_data_gateway.read_by_username(
            username, for_update=True
        )
        if user is None:
            raise UserNotFoundByUsername(username)

        await self._authorization_service.authorize_action_by_user(
            user, for_subordinate_only=True
        )

        self._user_service.change_password(user, password)
        await self._committer.commit()

        log.info("Change password: finished.")
        return ChangePasswordResponse(user.username.value, ResponseStatusEnum.UPDATED)
