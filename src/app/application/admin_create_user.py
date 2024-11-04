import logging
from dataclasses import dataclass

from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.committer import Committer
from app.application.common.ports.user_data_gateway import UserDataGateway
from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import RawPassword, Username
from app.domain.exceptions.user.existence import UsernameAlreadyExists
from app.domain.services.user import UserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    password: str
    role: UserRoleEnum


@dataclass(frozen=True, slots=True)
class CreateUserResponse:
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
        authorization_service: AuthorizationService,
        user_data_gateway: UserDataGateway,
        user_service: UserService,
        committer: Committer,
    ):
        self._authorization_service = authorization_service
        self._user_data_gateway = user_data_gateway
        self._user_service = user_service
        self._committer = committer

    async def __call__(self, request_data: CreateUserRequest) -> CreateUserResponse:
        log.info(
            "Create user by admin: started. Username: '%s'.", request_data.username
        )

        await self._authorization_service.authorize_action_by_role(
            request_data.role, for_subordinate_only=True
        )

        username: Username = Username(request_data.username)
        password: RawPassword = RawPassword(request_data.password)

        user: User = self._user_service.create_user(username, password)
        user.role = request_data.role

        try:
            await self._user_data_gateway.save(user)
        except UsernameAlreadyExists:
            raise

        await self._committer.commit()

        log.info("Create user by admin: finished. Username: '%s'.", user.username.value)
        return CreateUserResponse(user.username.value, ResponseStatusEnum.CREATED)
