from app.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)


class AnyOf[PC: PermissionContext](Permission[PC]):
    def __init__(self, *permissions: Permission[PC]) -> None:
        self._permissions = permissions

    def is_satisfied_by(self, context: PC) -> bool:
        return any(p.is_satisfied_by(context) for p in self._permissions)
