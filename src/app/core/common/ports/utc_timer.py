from abc import abstractmethod
from typing import Protocol

from app.core.common.value_objects.utc_datetime import UtcDatetime


class UtcTimer(Protocol):
    @property
    @abstractmethod
    def now(self) -> UtcDatetime: ...
