from dataclasses import dataclass, field
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainTypeError
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class RawPassword(ValueObject):
    """raises DomainTypeError"""

    MIN_LEN: ClassVar[Final[int]] = 6

    value: bytes = field(init=False, repr=False)

    def __init__(self, value: str) -> None:
        """:raises DomainTypeError:"""
        self._validate_password_length(value)
        object.__setattr__(self, "value", value.encode())

    def _validate_password_length(self, password_value: str) -> None:
        """:raises DomainTypeError:"""
        if len(password_value) < self.MIN_LEN:
            raise DomainTypeError(
                f"Password must be at least {self.MIN_LEN} characters long.",
            )
