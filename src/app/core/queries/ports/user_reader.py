from abc import abstractmethod
from typing import Protocol

from app.core.queries.models.user import ListUsersQm
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingParams


class UserReader(Protocol):
    @abstractmethod
    async def list_all(
        self,
        *,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQm: ...
