from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

    @property
    def is_assignable(self) -> bool:
        return self != UserRole.SUPER_ADMIN

    @property
    def is_changeable(self) -> bool:
        return self != UserRole.SUPER_ADMIN
