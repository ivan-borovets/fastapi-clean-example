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
    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        allowed_roles = ROLE_HIERARCHY.get(context.subject.role, set())
        return context.target.role in allowed_roles


@dataclass(frozen=True, slots=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject: User
    target_role: UserRole


class CanManageRole(Permission[RoleManagementContext]):
    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = ROLE_HIERARCHY.get(context.subject.role, set())
        return context.target_role in allowed_roles
