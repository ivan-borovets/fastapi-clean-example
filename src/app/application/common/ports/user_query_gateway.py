from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from app.application.common.query_params.offset_pagination import OffsetPaginationParams
from app.application.common.query_params.sorting import SortingParams
from app.domain.enums.user_role import UserRole


class UserQueryModel(TypedDict):
    id_: UUID
    username: str
    role: UserRole
    is_active: bool


class ListUsersQM(TypedDict):
    users: list[UserQueryModel]
    total: int


class UserQueryGateway(Protocol):
    @abstractmethod
    async def read_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
