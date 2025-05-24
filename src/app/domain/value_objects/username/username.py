from dataclasses import dataclass

from app.domain.value_objects.base import ValueObject
from app.domain.value_objects.username.validation import (
    validate_username_length,
    validate_username_pattern,
)


@dataclass(frozen=True, repr=False)
class Username(ValueObject):
    """raises DomainFieldError"""

    value: str

    def __post_init__(self) -> None:
        """
        :raises DomainFieldError:
        """
        super().__post_init__()

        validate_username_length(self.value)
        validate_username_pattern(self.value)
