from app.core.common.authorization.base import Permission
from tests.unit.core.common.authorization.types_ import DummyContext


class AlwaysAllow(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return True


class AlwaysDeny(Permission[DummyContext]):
    def is_satisfied_by(self, context: DummyContext) -> bool:
        return False
