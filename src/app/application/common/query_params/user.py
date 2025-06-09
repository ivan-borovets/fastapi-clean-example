from dataclasses import dataclass

from app.application.common.query_params.pagination import Pagination
from app.application.common.query_params.sorting import SortingOrder


@dataclass(frozen=True, slots=True, kw_only=True)
class UserListSorting:
    sorting_field: str
    sorting_order: SortingOrder


@dataclass(frozen=True, slots=True)
class UserListParams:
    pagination: Pagination
    sorting: UserListSorting
