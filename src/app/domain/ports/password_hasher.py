from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.user_password_hash import UserPasswordHash


class PasswordHasher(Protocol):
    @abstractmethod
    async def hash(self, raw_password: RawPassword) -> UserPasswordHash:
        """:raises PasswordHasherBusyError:"""

    @abstractmethod
    async def verify(
        self,
        raw_password: RawPassword,
        hashed_password: UserPasswordHash,
    ) -> bool:
        """:raises PasswordHasherBusyError:"""
