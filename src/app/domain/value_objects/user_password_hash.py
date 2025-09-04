from dataclasses import dataclass

from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserPasswordHash(ValueObject):
    value: bytes
