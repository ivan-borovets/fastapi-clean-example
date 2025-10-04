from dataclasses import dataclass, field
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class RawPassword(ValueObject):
    """raises DomainFieldError"""

    MIN_LEN: ClassVar[Final[int]] = 6

    value: bytes = field(init=False, repr=False)

    def __init__(self, value: str):
        """:raises DomainFieldError:"""
        self._validate_password_length(value)
        object.__setattr__(self, "value", value.encode())
        super(RawPassword, self).__post_init__()

    def _validate_password_length(self, password_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(password_value) < self.MIN_LEN:
            raise DomainFieldError(
                f"Password must be at least {self.MIN_LEN} characters long.",
            )
