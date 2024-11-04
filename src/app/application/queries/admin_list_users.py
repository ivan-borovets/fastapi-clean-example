import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.service import AuthorizationService
from app.application.common.exceptions.sorting import SortingError
from app.application.common.ports.query_gateways.user import UserQueryGateway
from app.application.common.query_filters.sorting_order_enum import SortingOrderEnum
from app.application.common.query_filters.user.read_all import (
    UserReadAllPagination,
    UserReadAllParams,
    UserReadAllSorting,
)
from app.application.common.query_models.user import UserQueryModel

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersRequest:
    limit: int
    offset: int
    sorting_field: str | None
    sorting_order: SortingOrderEnum | None


class ListUsersResponse(TypedDict):
    users: list[UserQueryModel]


class ListUsersQueryService:
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
    :raises PaginationError:
    :raises ReaderError:
    :raises SortingError:
    """

    def __init__(
        self,
        authorization_service: AuthorizationService,
        user_query_gateway: UserQueryGateway,
    ):
        self._authorization_service = authorization_service
        self._user_query_gateway = user_query_gateway

    async def __call__(self, request_data: ListUsersRequest) -> ListUsersResponse:
        log.info("List users by admin: started.")

        await self._authorization_service.authorize_action(PermissionEnum.MANAGE_USERS)

        log.debug("Retrieving list of users.")
        user_read_all_params: UserReadAllParams = UserReadAllParams(
            pagination=UserReadAllPagination(
                limit=request_data.limit,
                offset=request_data.offset,
            ),
            sorting=UserReadAllSorting(
                sorting_field=request_data.sorting_field or "username",
                sorting_order=request_data.sorting_order or SortingOrderEnum.ASC,
            ),
        )

        users: list[UserQueryModel] | None = await self._user_query_gateway.read_all(
            user_read_all_params
        )
        if users is None:
            log.error(
                "Retrieving list of users failed: invalid sorting column '%s'.",
                request_data.sorting_field,
            )
            raise SortingError("Invalid sorting field.")

        response: ListUsersResponse = ListUsersResponse(users=users)

        log.info("List users by admin: finished.")
        return response
