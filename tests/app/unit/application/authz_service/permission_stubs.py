from app.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)


class DummyContext(PermissionContext):
    pass


class AlwaysAllow(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return True


class AlwaysDeny(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return False
