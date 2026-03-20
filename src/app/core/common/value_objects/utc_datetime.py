from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.common.exceptions import BusinessTypeError
from app.core.common.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UtcDatetime(ValueObject):
    value: datetime

    def __post_init__(self) -> None:
        self._ensure_is_tz_aware(self.value)
        object.__setattr__(self, "value", self._normalize(self.value))

    @classmethod
    def _ensure_is_tz_aware(cls, dt: datetime) -> None:
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise BusinessTypeError(f"{cls.__name__}: timezone-aware datetime required, got {dt!r}")

    @classmethod
    def _normalize(cls, dt: datetime) -> datetime:
        return dt.astimezone(UTC)
