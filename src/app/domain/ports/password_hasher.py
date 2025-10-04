from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.raw_password import RawPassword


class PasswordHasher(Protocol):
    @abstractmethod
    async def hash(self, raw_password: RawPassword) -> bytes:
        """:raises PasswordHasherBusyError:"""

    @abstractmethod
    async def verify(
        self,
        raw_password: RawPassword,
        hashed_password: bytes,
    ) -> bool:
        """:raises PasswordHasherBusyError:"""
