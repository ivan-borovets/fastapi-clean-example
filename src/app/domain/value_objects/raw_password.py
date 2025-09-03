from dataclasses import dataclass
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, repr=False)
class RawPassword(ValueObject):
    """raises DomainFieldError"""

    value: str

    MIN_LEN: Final[ClassVar[int]] = 6

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super().__post_init__()
        self._validate_password_length(self.value)

    def _validate_password_length(self, password_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(password_value) < self.MIN_LEN:
            raise DomainFieldError(
                f"Password must be at least {self.MIN_LEN} characters long.",
            )
