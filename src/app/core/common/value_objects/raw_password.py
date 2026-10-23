from dataclasses import dataclass, field
from typing import ClassVar

from app.core.common.exceptions import BusinessTypeError
from app.core.common.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class RawPassword(ValueObject):
    MIN_LEN: ClassVar[int] = 6

    value: bytes = field(init=False, repr=False)

    def __init__(self, value: str) -> None:
        self._validate(value)
        object.__setattr__(self, "value", value.encode())

    @classmethod
    def _validate(cls, value: str) -> None:
        if len(value) < cls.MIN_LEN:
            raise BusinessTypeError(f"Password must be at least {cls.MIN_LEN} characters long.")
