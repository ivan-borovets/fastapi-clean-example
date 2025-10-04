import asyncio
import base64
import hashlib
import hmac
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import bcrypt

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.value_objects.raw_password import RawPassword
from app.infrastructure.adapters.types import HasherSemaphore, HasherThreadPoolExecutor

log = logging.getLogger(__name__)


class BcryptPasswordHasher(PasswordHasher):
    def __init__(
        self,
        pepper: bytes,
        work_factor: int,
        executor: HasherThreadPoolExecutor,
        semaphore: HasherSemaphore,
        semaphore_wait_timeout_s: float,
    ):
        self._pepper = pepper
        self._work_factor = work_factor
        self._executor = executor
        self._semaphore = semaphore
        self._semaphore_wait_timeout_s = semaphore_wait_timeout_s

    async def hash(self, raw_password: RawPassword) -> bytes:
        async with self._permit():
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self._executor,
                self.hash_sync,
                raw_password,
            )

    async def verify(self, raw_password: RawPassword, hashed_password: bytes) -> bool:
        async with self._permit():
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self._executor,
                self.verify_sync,
                raw_password,
                hashed_password,
            )

    @asynccontextmanager
    async def _permit(self) -> AsyncIterator[None]:
        await asyncio.wait_for(
            self._semaphore.acquire(),
            timeout=self._semaphore_wait_timeout_s,
        )
        try:
            yield
        finally:
            self._semaphore.release()

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
    def _add_pepper(raw_password: RawPassword, pepper: bytes) -> bytes:
        hmac_password: bytes = hmac.new(
            key=pepper,
            msg=raw_password.value,
            digestmod=hashlib.sha384,
        ).digest()
        return base64.b64encode(hmac_password)
