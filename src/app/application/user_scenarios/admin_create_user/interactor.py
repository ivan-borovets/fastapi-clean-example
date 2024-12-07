import logging

from app.application.base.interactors import InteractorStrict
from app.application.committer import Committer
from app.application.enums import ResponseStatusEnum
from app.application.user.ports.user_data_gateway import UserDataGateway
from app.application.user.service_authorization import AuthorizationService
from app.application.user_scenarios.admin_create_user.payload import (
    CreateUserRequest,
    CreateUserResponse,
)
from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.exceptions.existence import UsernameAlreadyExists
from app.domain.user.service import UserService
from app.domain.user.value_objects import RawPassword, Username

log = logging.getLogger(__name__)


class CreateUserInteractor(InteractorStrict[CreateUserRequest, CreateUserResponse]):
    """
    :raises AuthenticationError:
    :raises AuthorizationError:
    :raises DomainFieldError:
    :raises DataGatewayError:
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

        await self._authorization_service.check_authorization(UserRoleEnum.ADMIN)

        username: Username = Username(request_data.username)
        password: RawPassword = RawPassword(request_data.password)

        if not await self._user_data_gateway.is_username_unique(username):
            raise UsernameAlreadyExists(username.value)

        user: User = self._user_service.create_user(username, password)

        log.debug("Setting given roles.")
        user.roles = request_data.roles | {UserRoleEnum.USER}
        await self._user_data_gateway.save(user)

        await self._committer.commit()

        log.info("Create user by admin: finished. Username: '%s'.", user.username.value)
        return CreateUserResponse(user.username.value, ResponseStatusEnum.CREATED)
