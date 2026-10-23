from dataclasses import dataclass

from app.core.common.authorization.base import PermissionContext


@dataclass(frozen=True, slots=True)
class DummyContext(PermissionContext):
    pass
