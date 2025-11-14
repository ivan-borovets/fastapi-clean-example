import logging
from dataclasses import dataclass

from app.application.common.ports.user_query_gateway import (
    ListUsersQM,
    UserQueryGateway,
)
from app.application.common.query_params.offset_pagination import OffsetPaginationParams
from app.application.common.query_params.sorting import SortingOrder, SortingParams
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.enums.user_role import UserRole

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ListUsersRequest:
    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ListUsersQueryService:
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_query_gateway: UserQueryGateway,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_query_gateway = user_query_gateway

    async def execute(self, request_data: ListUsersRequest) -> ListUsersQM:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises PaginationError:
        :raises SortingError:
        :raises ReaderError:
        """
        log.info("List users: started.")

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )

        log.debug("Retrieving list of users.")
        pagination = OffsetPaginationParams(
            limit=request_data.limit,
            offset=request_data.offset,
        )
        sorting = SortingParams(
            field=request_data.sorting_field,
            order=request_data.sorting_order,
        )
        response = await self._user_query_gateway.read_all(
            pagination=pagination,
            sorting=sorting,
        )

        log.info("List users: done.")
        return response
