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
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.infrastructure.adapters.types import HasherSemaphore, HasherThreadPoolExecutor
from app.infrastructure.exceptions.password_hasher import PasswordHasherBusyError

log = logging.getLogger(__name__)


class BcryptPasswordHasher(PasswordHasher):
    def __init__(
        self,
        pepper: bytes,
        work_factor: int,
        executor: HasherThreadPoolExecutor,
        semaphore: HasherSemaphore,
        semaphore_wait_timeout_s: float,
    ) -> None:
        self._pepper = pepper
        self._work_factor = work_factor
        self._executor = executor
        self._semaphore = semaphore
        self._semaphore_wait_timeout_s = semaphore_wait_timeout_s

    async def hash(self, raw_password: RawPassword) -> UserPasswordHash:
        """:raises PasswordHasherBusyError:"""
        async with self._permit():
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self._executor,
                self.hash_sync,
                raw_password,
            )

    async def verify(
        self,
        raw_password: RawPassword,
        hashed_password: UserPasswordHash,
    ) -> bool:
        """:raises PasswordHasherBusyError:"""
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
        """:raises PasswordHasherBusyError:"""
        try:
            await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=self._semaphore_wait_timeout_s,
            )
        except TimeoutError as err:
            raise PasswordHasherBusyError from err
        try:
            yield
        finally:
            self._semaphore.release()

    def hash_sync(self, raw_password: RawPassword) -> UserPasswordHash:
        """
        Pre-hashing:
        https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pre-hashing-passwords-with-bcrypt
        Work factor:
        https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#introduction
        """
        log.debug("hash")
        base64_hmac_peppered = self._add_pepper(raw_password, self._pepper)
        salt = bcrypt.gensalt(rounds=self._work_factor)
        return UserPasswordHash(bcrypt.hashpw(base64_hmac_peppered, salt))

    def verify_sync(
        self, raw_password: RawPassword, hashed_password: UserPasswordHash
    ) -> bool:
        log.debug("verify")
        base64_hmac_peppered = self._add_pepper(raw_password, self._pepper)
        return bcrypt.checkpw(base64_hmac_peppered, hashed_password.value)

    @staticmethod
    def _add_pepper(raw_password: RawPassword, pepper: bytes) -> bytes:
        hmac_password = hmac.new(
            key=pepper,
            msg=raw_password.value,
            digestmod=hashlib.sha384,
        ).digest()
        return base64.b64encode(hmac_password)
