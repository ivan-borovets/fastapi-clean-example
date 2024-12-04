import logging

from app.application.base.interactors import InteractorStrict
from app.application.committer import Committer
from app.application.enums import ResponseStatusEnum
from app.application.user.ports.user_data_gateway import UserDataGateway
from app.application.user.service_authorization import AuthorizationService
from app.application_scenarios.admin_reactivate_user.payload import (
    ReactivateUserRequest,
    ReactivateUserResponse,
)
from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.exceptions.non_existence import UserNotFoundByUsername
from app.domain.user.service import UserService
from app.domain.user.value_objects import Username

log = logging.getLogger(__name__)


class ReactivateUserInteractor(
    InteractorStrict[ReactivateUserRequest, ReactivateUserResponse]
):
    """
    :raises AuthenticationError:
    :raises AuthorizationError:
    :raises DomainFieldError:
    :raises DataGatewayError:
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
            "Reactivate admin by admin: started. Username: '%s'.", request_data.username
        )

        await self._authorization_service.check_authorization(UserRoleEnum.ADMIN)

        username: Username = Username(request_data.username)

        user: User | None = await self._user_data_gateway.read_by_username(
            username, for_update=True
        )
        if user is None:
            raise UserNotFoundByUsername(username)

        self._user_service.toggle_user_activation(user, True)
        await self._committer.commit()

        log.info(
            "Reactivate admin by admin: finished. Username: '%s'.", user.username.value
        )
        return ReactivateUserResponse(user.username.value, ResponseStatusEnum.UPDATED)
