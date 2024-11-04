import logging

from app.application.base.interactors import InteractorStrict
from app.application.enums import ResponseStatusEnum
from app.application.user.protocols.admin_user_service import AdminUserService
from app.application.user.services.authorization import AuthorizationService
from app.domain.user.entity_user import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.vo_user import Username
from app.scenarios.user.create_user.application_payload import (
    CreateUserRequest,
    CreateUserResponse,
)

log = logging.getLogger(__name__)


class CreateUserInteractor(InteractorStrict[CreateUserRequest, CreateUserResponse]):
    """
    :raises AuthenticationError:
    :raises AuthorizationError:
    :raises DataGatewayError:
    :raises UsernameAlreadyExists:
    """

    def __init__(
        self,
        authorization_service: AuthorizationService,
        admin_user_service: AdminUserService,
    ):
        self._authorization_service = authorization_service
        self._admin_user_service = admin_user_service

    async def __call__(self, request_data: CreateUserRequest) -> CreateUserResponse:
        log.info(
            "Create user by admin: started. Username: '%s'.", request_data.username
        )
        await self._authorization_service.authorize_and_try_prolong(UserRoleEnum.ADMIN)

        username_vo: Username = Username(request_data.username)

        await self._admin_user_service.check_username_uniqueness(username=username_vo)
        user: User = await self._admin_user_service.create_user(
            username_vo, request_data.password
        )

        log.debug("Setting given roles.")
        user.roles = request_data.roles | {UserRoleEnum.USER}

        await self._admin_user_service.save_user(user)
        log.info("Create user by admin: finished. Username: '%s'.", user.username.value)
        return CreateUserResponse(user.username.value, ResponseStatusEnum.CREATED)
