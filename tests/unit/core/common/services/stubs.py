import hashlib

from app.core.common.entities.types_ import UserPasswordHash
from app.core.common.ports.password_hasher import PasswordHasher
from app.core.common.value_objects.raw_password import RawPassword


class StubPasswordHasher(PasswordHasher):
    async def hash(self, raw_password: RawPassword) -> UserPasswordHash:
        return UserPasswordHash(hashlib.sha256(raw_password.value).digest())

    async def verify(self, raw_password: RawPassword, hashed_password: UserPasswordHash) -> bool:
        return await self.hash(raw_password) == hashed_password
