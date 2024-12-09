import logging

from app.application.base.interactors import InteractorStrict
from app.application.user.ports.user_data_gateway import UserDataGateway
from app.application.user.scenarios.admin_list_users.payload import (
    ListUsersRequest,
    ListUsersResponse,
    ListUsersResponseElement,
)
from app.application.user.services.authorization import AuthorizationService
from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum

log = logging.getLogger(__name__)


class ListUsersInteractor(InteractorStrict[ListUsersRequest, ListUsersResponse]):
    """
    :raises AuthenticationError:
    :raises AuthorizationError:
    :raises DataMapperError:
    """

    def __init__(
        self,
        authorization_service: AuthorizationService,
        user_data_gateway: UserDataGateway,
    ):
        self._authorization_service = authorization_service
        self._user_data_gateway = user_data_gateway

    async def __call__(self, request_data: ListUsersRequest) -> ListUsersResponse:
        log.info("List users by admin: started.")

        await self._authorization_service.check_authorization(UserRoleEnum.ADMIN)

        log.debug("Retrieving list of users.")
        users: list[User] = await self._user_data_gateway.read_all(
            request_data.limit, request_data.offset
        )

        response: ListUsersResponse = ListUsersResponse(
            [
                ListUsersResponseElement(
                    user.id_.value,
                    user.username.value,
                    user.roles,
                    user.is_active,
                )
                for user in users
            ]
        )

        log.info("List users by admin: finished.")
        return response
