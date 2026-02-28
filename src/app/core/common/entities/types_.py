from enum import StrEnum
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
UserPasswordHash = NewType("UserPasswordHash", bytes)


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

    @property
    def is_system(self) -> bool:
        return self == UserRole.SUPER_ADMIN
