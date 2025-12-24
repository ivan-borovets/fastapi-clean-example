import uuid
from dataclasses import dataclass
from uuid import UUID

from app.domain.value_objects.base import ValueObject
from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username import Username


@dataclass(frozen=True, slots=True, repr=False)
class SingleFieldVO(ValueObject):
    value: int


@dataclass(frozen=True, slots=True, repr=False)
class MultiFieldVO(ValueObject):
    value1: int
    value2: str


def create_single_field_vo(value: int = 1) -> SingleFieldVO:
    return SingleFieldVO(value)


def create_multi_field_vo(value1: int = 1, value2: str = "Alice") -> MultiFieldVO:
    return MultiFieldVO(value1, value2)


def create_user_id(value: UUID | None = None) -> UserId:
    return UserId(value if value else uuid.uuid4())


def create_username(value: str = "Alice") -> Username:
    return Username(value)


def create_raw_password(value: str = "Good Password") -> RawPassword:
    return RawPassword(value)


def create_password_hash(value: bytes = b"password_hash") -> UserPasswordHash:
    return UserPasswordHash(value)
