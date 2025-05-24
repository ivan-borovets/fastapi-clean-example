from dataclasses import dataclass

from app.domain.value_objects.base import ValueObject
from app.domain.value_objects.raw_password.validation import validate_password_length


@dataclass(frozen=True, repr=False)
class RawPassword(ValueObject):
    """raises DomainFieldError"""

    value: str

    def __post_init__(self) -> None:
        """
        :raises DomainFieldError:
        """
        super().__post_init__()

        validate_password_length(self.value)
