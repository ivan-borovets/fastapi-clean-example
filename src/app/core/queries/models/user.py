from datetime import datetime
from typing import TypedDict
from uuid import UUID


class UserQm(TypedDict):
    id: UUID
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ListUsersQm(TypedDict):
    users: list[UserQm]
    total: int
    limit: int
    offset: int
