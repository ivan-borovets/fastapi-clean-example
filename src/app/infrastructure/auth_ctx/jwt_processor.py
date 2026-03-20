from typing import Any, ClassVar

import jwt

from app.infrastructure.auth_ctx.jwt_types import JwtAlgorithm
from app.infrastructure.auth_ctx.model import AuthSession, SessionId


class JwtProcessor:
    SESSION_ID_CLAIM: ClassVar[str] = "sid"
    EXPIRATION_CLAIM: ClassVar[str] = "exp"

    def __init__(self, secret: str, algorithm: JwtAlgorithm) -> None:
        self._secret = secret
        self._algorithm = algorithm

    def encode(self, auth_session: AuthSession) -> str:
        payload: dict[str, Any] = {
            self.SESSION_ID_CLAIM: auth_session.id_,
            self.EXPIRATION_CLAIM: auth_session.expiration.value.timestamp(),
        }
        return jwt.encode(payload, key=self._secret, algorithm=self._algorithm)

    def decode_session_id(self, token: str) -> SessionId | None:
        try:
            payload = jwt.decode(token, key=self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError:
            return None

        value = payload.get(self.SESSION_ID_CLAIM)
        if not isinstance(value, str):
            return None
        return SessionId(value)
