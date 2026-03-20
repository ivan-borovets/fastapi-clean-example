from collections.abc import Mapping
from dataclasses import dataclass

from app.core.common.authorization.base import Permission, PermissionContext
from app.core.common.authorization.role_hierarchy import ROLE_HIERARCHY
from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User


@dataclass(frozen=True, slots=True, kw_only=True)
class UserManagementContext(PermissionContext):
    subject: User
    target: User


class CanManageSelf(Permission[UserManagementContext]):
    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        return context.subject == context.target


class CanManageSubordinate(Permission[UserManagementContext]):
    def __init__(self, role_hierarchy: Mapping[UserRole, set[UserRole]] = ROLE_HIERARCHY) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target.role in allowed_roles


@dataclass(frozen=True, slots=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject: User
    target_role: UserRole


class CanManageRole(Permission[RoleManagementContext]):
    def __init__(self, role_hierarchy: Mapping[UserRole, set[UserRole]] = ROLE_HIERARCHY) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        return context.target_role in allowed_roles
