from abc import abstractmethod
from typing import Protocol

from app.core.common.entities.types_ import UserPasswordHash
from app.core.common.value_objects.raw_password import RawPassword


class PasswordHasher(Protocol):
    @abstractmethod
    async def hash(self, raw_password: RawPassword) -> UserPasswordHash: ...

    @abstractmethod
    async def verify(self, raw_password: RawPassword, hashed_password: UserPasswordHash) -> bool: ...
