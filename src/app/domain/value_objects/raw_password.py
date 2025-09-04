from dataclasses import dataclass
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class RawPassword(ValueObject):
    """raises DomainFieldError"""

    MIN_LEN: ClassVar[Final[int]] = 6

    value: str

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(RawPassword, self).__post_init__()
        self._validate_password_length(self.value)

    def _validate_password_length(self, password_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(password_value) < self.MIN_LEN:
            raise DomainFieldError(
                f"Password must be at least {self.MIN_LEN} characters long.",
            )
