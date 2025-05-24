from dataclasses import dataclass

from app.application.common.exceptions.pagination import PaginationError
from app.application.common.query_filters.sorting_order_enum import SortingOrder


@dataclass(frozen=True, slots=True, kw_only=True)
class UserReadAllPagination:
    """
    :raises PaginationError:
    """

    limit: int
    offset: int

    def __post_init__(self):
        if self.limit <= 0:
            raise PaginationError(f"Limit must be greater than 0, got {self.limit}")
        if self.offset < 0:
            raise PaginationError(f"Offset must be non-negative, got {self.offset}")


@dataclass(frozen=True, slots=True, kw_only=True)
class UserReadAllSorting:
    sorting_field: str
    sorting_order: SortingOrder


@dataclass(frozen=True, slots=True)
class UserReadAllParams:
    pagination: UserReadAllPagination
    sorting: UserReadAllSorting
