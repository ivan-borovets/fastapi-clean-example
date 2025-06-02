from collections.abc import Mapping
from typing import Final

from app.application.common.constants import AUTHZ_NOT_AUTHORIZED
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.enums.user_role import UserRole
from app.domain.value_objects.user_id import UserId

SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPER_ADMIN: {UserRole.ADMIN, UserRole.USER},
    UserRole.ADMIN: {UserRole.USER},
    UserRole.USER: set(),
}


class AuthorizationService:
    def authorize_for_self(
        self,
        current_user_id: UserId,
        /,
        *,
        target_id: UserId,
    ) -> None:
        """
        :raises AuthorizationError:
        """
        if current_user_id != target_id:
            raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)

    def authorize_for_subordinate_role(
        self,
        current_user_role: UserRole,
        /,
        *,
        target_role: UserRole,
    ) -> None:
        """
        :raises AuthorizationError:
        """
        allowed_roles = SUBORDINATE_ROLES.get(current_user_role, set())
        if target_role not in allowed_roles:
            raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)
