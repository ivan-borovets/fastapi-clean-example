import asyncio
import base64
import hashlib
import hmac
import logging

import bcrypt

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.value_objects.raw_password import RawPassword
from app.infrastructure.adapters.types import HasherThreadPoolExecutor

log = logging.getLogger(__name__)


class BcryptPasswordHasher(PasswordHasher):
    def __init__(
        self,
        pepper: str,
        work_factor: int,
        executor: HasherThreadPoolExecutor,
    ):
        self._pepper = pepper
        self._work_factor = work_factor
        self._executor = executor

    async def hash(self, raw_password: RawPassword) -> bytes:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self.hash_sync, raw_password)

    async def verify(self, raw_password: RawPassword, hashed_password: bytes) -> bool:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self.verify_sync,
            raw_password,
            hashed_password,
        )

    def hash_sync(self, raw_password: RawPassword) -> bytes:
        """
        Pre-hashing:
        https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pre-hashing-passwords-with-bcrypt
        Work factor:
        https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#introduction
        """
        log.debug("hash")
        base64_hmac_peppered: bytes = self._add_pepper(raw_password, self._pepper)
        salt: bytes = bcrypt.gensalt(rounds=self._work_factor)
        return bcrypt.hashpw(base64_hmac_peppered, salt)

    def verify_sync(self, raw_password: RawPassword, hashed_password: bytes) -> bool:
        log.debug("verify")
        base64_hmac_peppered: bytes = self._add_pepper(raw_password, self._pepper)
        return bcrypt.checkpw(base64_hmac_peppered, hashed_password)

    @staticmethod
    def _add_pepper(raw_password: RawPassword, pepper: str) -> bytes:
        hmac_password: bytes = hmac.new(
            key=pepper.encode(),
            msg=raw_password.value.encode(),
            digestmod=hashlib.sha384,
        ).digest()
        return base64.b64encode(hmac_password)
