"""Permission policies for declarative authorization."""

from abc import ABC, abstractmethod
from typing import Any

from app.application.common.services.authorization import SUBORDINATE_ROLES
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole


class Permission(ABC):
    """Base class for a permission policy."""

    @abstractmethod
    def is_satisfied_by(self, current_user: User, **kwargs: Any) -> bool:
        """Check if the permission is satisfied for the given user and context."""
        ...


class IsSelf(Permission):
    """Permission that checks if the user is acting on themselves."""

    def is_satisfied_by(
        self, current_user: User, *, target_user: User, **kwargs: Any
    ) -> bool:
        """Check if current user is the same as target user."""
        _ = kwargs  # Unused but required for interface
        return current_user.id_ == target_user.id_


class IsSuperior(Permission):
    """Permission that checks if the user has a superior role over the target."""

    def is_satisfied_by(
        self, current_user: User, *, target_user: User, **kwargs: Any
    ) -> bool:
        """Check if current user's role is superior to target user's role."""
        _ = kwargs  # Unused but required for interface
        allowed_roles = SUBORDINATE_ROLES.get(current_user.role, set())
        return target_user.role in allowed_roles


class AnyOf(Permission):
    """Composite permission that is satisfied if ANY sub-permission is satisfied."""

    def __init__(self, *permissions: Permission) -> None:
        """Initialize with a list of permissions to check."""
        self._permissions = permissions

    def is_satisfied_by(self, current_user: User, **kwargs: Any) -> bool:
        """Check if any of the sub-permissions is satisfied."""
        return any(p.is_satisfied_by(current_user, **kwargs) for p in self._permissions)


class AllOf(Permission):
    """Composite permission that is satisfied if ALL sub-permissions are satisfied."""

    def __init__(self, *permissions: Permission) -> None:
        """Initialize with a list of permissions to check."""
        self._permissions = permissions

    def is_satisfied_by(self, current_user: User, **kwargs: Any) -> bool:
        """Check if all of the sub-permissions are satisfied."""
        return all(p.is_satisfied_by(current_user, **kwargs) for p in self._permissions)


class CanManageRole(Permission):
    """Permission that checks if the user can manage a specific role."""

    def __init__(self, target_role: UserRole) -> None:
        """Initialize with the role to manage."""
        self._target_role = target_role

    def is_satisfied_by(self, current_user: User, **kwargs: Any) -> bool:
        """Check if current user can manage the target role."""
        _ = kwargs  # Unused but required for interface
        allowed_roles = SUBORDINATE_ROLES.get(current_user.role, set())
        return self._target_role in allowed_roles
