from collections.abc import Mapping
from typing import Final

from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole

SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPER_ADMIN: {UserRole.ADMIN, UserRole.USER},
    UserRole.ADMIN: {UserRole.USER},
    UserRole.USER: set(),
}


class AuthorizationService:
    def authorize_for_self(self, current_user: User, /, *, target_user: User) -> None:
        """
        :raises AuthorizationError:
        """
        if current_user.id_ != target_user.id_:
            raise AuthorizationError("Not authorized.")

    def authorize_for_subordinate_role(
        self,
        current_user: User,
        /,
        *,
        target_role: UserRole,
    ) -> None:
        """
        :raises AuthorizationError:
        """
        allowed_roles = SUBORDINATE_ROLES.get(current_user.role, set())
        if target_role not in allowed_roles:
            raise AuthorizationError("Not authorized.")
