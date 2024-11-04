from dataclasses import dataclass
from uuid import UUID

from app.base.a_domain.value_object import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class Username(ValueObject):
    value: str


@dataclass(frozen=True, slots=True, repr=False)
class UserPasswordHash(ValueObject):
    value: bytes
