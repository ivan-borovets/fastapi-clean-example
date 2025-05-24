from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.raw_password.raw_password import RawPassword


class PasswordHasher(Protocol):
    @abstractmethod
    def hash(self, raw_password: RawPassword) -> bytes: ...

    @abstractmethod
    def verify(self, *, raw_password: RawPassword, hashed_password: bytes) -> bool: ...
