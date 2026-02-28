from dataclasses import dataclass

from app.core.common.authorization.base import Permission, PermissionContext


@dataclass(frozen=True, slots=True)
class DummyContext(PermissionContext):
    pass


class AlwaysAllow(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return True


class AlwaysDeny(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return False
