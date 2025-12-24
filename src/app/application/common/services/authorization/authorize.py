from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)
from app.application.common.services.constants import AUTHZ_NOT_AUTHORIZED


def authorize[PC: PermissionContext](
    permission: Permission[PC],
    *,
    context: PC,
) -> None:
    """:raises AuthorizationError:"""
    if not permission.is_satisfied_by(context):
        raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)
