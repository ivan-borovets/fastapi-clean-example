from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.base.value_object import ValueObject
from app.domain.entities.user.validation.functions import (
    validate_password_length,
    validate_username_length,
    validate_username_pattern,
)


@dataclass(frozen=True, repr=False)
class UserId(ValueObject):
    value: UUID


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


@dataclass(frozen=True, repr=False)
class UserPasswordHash(ValueObject):
    value: bytes


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
