from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionContext:
    pass


class Permission[PC: PermissionContext](ABC):
    @abstractmethod
    def is_satisfied_by(self, context: PC) -> bool: ...
