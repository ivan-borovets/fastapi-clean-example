from typing import TypedDict
from uuid import UUID

from app.domain.entities.user.role_enum import UserRoleEnum


class UserQueryModel(TypedDict):
    id_: UUID
    username: str
    role: UserRoleEnum
    is_active: bool
