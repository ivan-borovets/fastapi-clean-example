from collections.abc import Mapping
from typing import Final

from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum

SUBORDINATE_ROLES: Final[Mapping[UserRoleEnum, set[UserRoleEnum]]] = {
    UserRoleEnum.SUPER_ADMIN: {UserRoleEnum.ADMIN, UserRoleEnum.USER},
    UserRoleEnum.ADMIN: {UserRoleEnum.USER},
    UserRoleEnum.USER: set(),
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
        target_role: UserRoleEnum,
    ) -> None:
        """
        :raises AuthorizationError:
        """
        allowed_roles = SUBORDINATE_ROLES.get(current_user.role, set())
        if target_role not in allowed_roles:
            raise AuthorizationError("Not authorized.")
