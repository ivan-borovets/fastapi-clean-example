import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.exceptions.query import SortingError
from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.query_models.user import UserQueryModel
from app.application.common.query_params.pagination import Pagination
from app.application.common.query_params.sorting import SortingOrder
from app.application.common.query_params.user import (
    UserListParams,
    UserListSorting,
)
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.domain.enums.user_role import UserRole

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersRequest:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ListUsersResponse(TypedDict):
    users: list[UserQueryModel]


class ListUsersQueryService:
    """
    Open to admins.
    Retrieves a paginated list of existing users with relevant information.

    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
    :raises ReaderError:
    :raises PaginationError:
    :raises SortingError:
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        authorization_service: AuthorizationService,
        user_query_gateway: UserQueryGateway,
    ):
        self._current_user_service = current_user_service
        self._authorization_service = authorization_service
        self._user_query_gateway = user_query_gateway

    async def __call__(self, request_data: ListUsersRequest) -> ListUsersResponse:
        log.info("List users: started.")

        current_user = await self._current_user_service.get_current_user()
        self._authorization_service.authorize_for_subordinate_role(
            current_user.role,
            target_role=UserRole.USER,
        )

        log.debug("Retrieving list of users.")
        user_list_params = UserListParams(
            pagination=Pagination(
                limit=request_data.limit,
                offset=request_data.offset,
            ),
            sorting=UserListSorting(
                sorting_field=request_data.sorting_field,
                sorting_order=request_data.sorting_order,
            ),
        )

        users: list[UserQueryModel] | None = await self._user_query_gateway.read_all(
            user_list_params,
        )
        if users is None:
            log.error(
                "Retrieving list of users failed: invalid sorting column '%s'.",
                request_data.sorting_field,
            )
            raise SortingError("Invalid sorting field.")

        response = ListUsersResponse(users=users)

        log.info("List users: done.")
        return response
