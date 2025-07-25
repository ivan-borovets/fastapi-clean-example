import base64
import hashlib
import hmac
from typing import NewType

import bcrypt

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.value_objects.raw_password.raw_password import RawPassword

PasswordPepper = NewType("PasswordPepper", str)


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self, pepper: PasswordPepper):
        self._pepper = pepper

    def hash(self, raw_password: RawPassword) -> bytes:
        """
        Bcrypt is limited to 72-character passwords. Adding a pepper may surpass this character count.
        To keep the input within the 72-character limit, pre-hashing can be employed.
        One option is using HMAC-SHA256, which produces a fixed-length digest of the peppered password.
        However, pre-hashing may introduce null bytes, which `bcrypt` cannot process correctly.
        This issue can be resolved by applying `base64` encoding to the digest.
        The resulting `base64(hmac-sha256(password, pepper))` string is then ready for bcrypt hashing.
        Salt is added to this string before passing it to `bcrypt` for the final hashing step.
        Inspired by: https://blog.ircmaxell.com/2015/03/security-issue-combining-bcrypt-with.html
        """
        base64_hmac_password: bytes = self._add_pepper(raw_password, self._pepper)
        salt: bytes = bcrypt.gensalt()
        return bcrypt.hashpw(base64_hmac_password, salt)

    @staticmethod
    def _add_pepper(raw_password: RawPassword, pepper: PasswordPepper) -> bytes:
        hmac_password: bytes = hmac.new(
            key=pepper.encode(),
            msg=raw_password.value.encode(),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(hmac_password)

    def verify(self, *, raw_password: RawPassword, hashed_password: bytes) -> bool:
        base64_hmac_password: bytes = self._add_pepper(raw_password, self._pepper)
        return bcrypt.checkpw(base64_hmac_password, hashed_password)
