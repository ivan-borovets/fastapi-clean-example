from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PermissionContext:
    pass


class Permission[PC: PermissionContext](Protocol):
    @abstractmethod
    def is_satisfied_by(self, context: PC) -> bool: ...
