import logging
from dataclasses import dataclass
from uuid import UUID

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.service import AuthorizationService
from app.application.common.ports.user_data_gateway import UserDataGateway
from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersRequest:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class ListUsersResponseElement:
    id: UUID
    username: str
    role: UserRoleEnum
    is_active: bool


@dataclass(frozen=True, slots=True)
class ListUsersResponse:
    users: list[ListUsersResponseElement]


class ListUsersInteractor:
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
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

        await self._authorization_service.authorize_action(PermissionEnum.MANAGE_USERS)

        log.debug("Retrieving list of users.")
        users: list[User] = await self._user_data_gateway.read_all(
            request_data.limit, request_data.offset
        )

        response: ListUsersResponse = ListUsersResponse(
            [
                ListUsersResponseElement(
                    user.id_.value,
                    user.username.value,
                    user.role,
                    user.is_active,
                )
                for user in users
            ]
        )

        log.info("List users by admin: finished.")
        return response
