from enum import StrEnum
from typing import Final, Mapping

from app.domain.entities.user.role_enum import UserRoleEnum

ROLE_HIERARCHY: Final[Mapping[UserRoleEnum, set[UserRoleEnum]]] = {
    UserRoleEnum.SUPER_ADMIN: {UserRoleEnum.ADMIN},
    UserRoleEnum.ADMIN: {UserRoleEnum.USER},
    UserRoleEnum.USER: set(),
}


class PermissionEnum(StrEnum):
    ALL = "all"
    MANAGE_USERS = "manage_users"
    EDIT_SELF = "edit_self"


ROLE_PERMISSIONS: Final[Mapping[UserRoleEnum, set[PermissionEnum]]] = {
    UserRoleEnum.SUPER_ADMIN: {PermissionEnum.ALL},
    UserRoleEnum.ADMIN: {PermissionEnum.MANAGE_USERS},
    UserRoleEnum.USER: {PermissionEnum.EDIT_SELF},
}
