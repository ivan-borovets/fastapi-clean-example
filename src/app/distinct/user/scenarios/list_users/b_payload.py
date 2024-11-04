from dataclasses import dataclass
from uuid import UUID

from app.common.b_application.request_data.pagination import PaginationRequest
from app.distinct.user.a_domain.enums import UserRoleEnum


@dataclass(frozen=True)
class ListUsersRequest(PaginationRequest):
    __slots__ = ()


@dataclass(frozen=True, slots=True)
class ListUsersResponseElement:
    id: UUID
    username: str
    roles: set[UserRoleEnum]
    is_active: bool


@dataclass(frozen=True, slots=True)
class ListUsersResponse:
    users: list[ListUsersResponseElement]
