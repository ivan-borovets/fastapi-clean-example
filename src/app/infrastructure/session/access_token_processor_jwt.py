from typing import Any, cast

import jwt

from app.infrastructure.custom_types import JwtAlgorithm, JwtSecret
from app.infrastructure.exceptions import AdapterError
from app.infrastructure.session.session_timer_utc import UtcSessionTimer


class JwtAccessTokenProcessor:
    def __init__(
        self,
        secret: JwtSecret,
        algorithm: JwtAlgorithm,
        utc_session_timer: UtcSessionTimer,
    ):
        self._secret = secret
        self._algorithm = algorithm
        self._utc_session_timer = utc_session_timer

    def issue_access_token(self, session_id: str) -> str:
        to_encode: dict[str, Any] = {
            "session_id": session_id,
            "exp": int(self._utc_session_timer.access_expiration.timestamp()),
        }
        return jwt.encode(
            payload=to_encode,
            key=self._secret,
            algorithm=self._algorithm,
        )

    def extract_session_id(self, access_token: str) -> str:
        """
        :raises AdapterError:
        """
        payload: dict[str, Any] = self._decode_token(access_token)

        session_id: str | None = payload.get("session_id")
        if session_id is None:
            raise AdapterError("Token has no Session id.")

        return session_id

    def _decode_token(self, token: str) -> dict[str, Any]:
        """
        :raises AdapterError:
        """
        try:
            return cast(
                dict[str, Any],
                jwt.decode(
                    jwt=token,
                    key=self._secret,
                    algorithms=[self._algorithm],
                ),
            )
        except jwt.PyJWTError as error:
            raise AdapterError("Token is invalid or expired.") from error
