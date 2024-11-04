from typing import Mapping

from app.application.common.authorization.config import PermissionEnum
from app.domain.entities.user.role_enum import UserRoleEnum


class RolePermissionResolver:
    def __init__(
        self,
        role_hierarchy: Mapping[UserRoleEnum, set[UserRoleEnum]],
        role_permissions: Mapping[UserRoleEnum, set[PermissionEnum]],
    ):
        self._role_hierarchy = role_hierarchy
        self._role_permissions = role_permissions

    def compute_transitive_roles(
        self,
        role: UserRoleEnum,
    ) -> set[UserRoleEnum]:
        transitive_roles: set[UserRoleEnum] = {role}
        roles_to_process: list[UserRoleEnum] = [role]

        while roles_to_process:
            current_role: UserRoleEnum = roles_to_process.pop()
            sub_roles: set[UserRoleEnum] = self._role_hierarchy.get(current_role, set())

            new_roles: set[UserRoleEnum] = sub_roles - transitive_roles
            transitive_roles.update(new_roles)
            roles_to_process.extend(new_roles)

        return transitive_roles

    def compute_transitive_permissions(
        self,
        transitive_roles: set[UserRoleEnum],
    ) -> set[PermissionEnum]:
        permissions = set()

        for role in transitive_roles:
            permissions.update(self._role_permissions.get(role, set()))

        return permissions
