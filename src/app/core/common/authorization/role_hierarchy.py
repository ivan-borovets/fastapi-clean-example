from collections.abc import Mapping
from typing import Final

from app.core.common.entities.types_ import UserRole

ROLE_HIERARCHY: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPER_ADMIN: {UserRole.ADMIN, UserRole.USER},
    UserRole.ADMIN: {UserRole.USER},
    UserRole.USER: set(),
}
