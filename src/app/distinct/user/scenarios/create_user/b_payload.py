from dataclasses import dataclass

from app.common.b_application.enums import ResponseStatusEnum
from app.distinct.user.a_domain.enums import UserRoleEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    password: str
    roles: set[UserRoleEnum]


@dataclass(frozen=True, slots=True)
class CreateUserResponse:
    username: str
    status: ResponseStatusEnum
