import logging
from dataclasses import dataclass
from enum import StrEnum

from app.core.common.authorization.authorize import authorize
from app.core.common.authorization.current_user_service import CurrentUserService
from app.core.common.authorization.permissions import CanManageRole, RoleManagementContext
from app.core.common.entities.types_ import UserRole
from app.core.queries.ports.user_reader import ListUsersQm, UserReader
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingOrder, SortingParams

logger = logging.getLogger(__name__)


class UserSortingField(StrEnum):
    USERNAME = "username"
    ROLE = "role"
    IS_ACTIVE = "is_active"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersRequest:
    limit: int
    offset: int
    sorting_field: UserSortingField
    sorting_order: SortingOrder


class ListUsers:
    """
    - Open to admins.
    - Retrieves paginated list of existing users with relevant info.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_reader: UserReader,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_reader = user_reader

    async def execute(self, request: ListUsersRequest) -> ListUsersQm:
        logger.info("List users: started.")

        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )
        pagination = OffsetPaginationParams(
            limit=request.limit,
            offset=request.offset,
        )
        sorting = SortingParams(
            field=request.sorting_field,
            order=request.sorting_order,
        )
        users = await self._user_reader.list_users(
            pagination=pagination,
            sorting=sorting,
        )

        logger.info("List users: done.")
        return users
