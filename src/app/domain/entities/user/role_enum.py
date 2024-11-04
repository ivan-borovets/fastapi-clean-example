from enum import StrEnum


class UserRoleEnum(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"
