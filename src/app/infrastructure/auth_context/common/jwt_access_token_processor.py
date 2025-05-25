import logging
from typing import Any, cast

import jwt

from app.infrastructure.auth_context.common.new_types import JwtAlgorithm, JwtSecret
from app.infrastructure.auth_context.common.utc_auth_session_timer import (
    UtcAuthSessionTimer,
)

log = logging.getLogger(__name__)


class JwtAccessTokenProcessor:
    def __init__(
        self,
        secret: JwtSecret,
        algorithm: JwtAlgorithm,
        utc_auth_session_timer: UtcAuthSessionTimer,
    ):
        self._secret = secret
        self._algorithm = algorithm
        self._utc_auth_session_timer = utc_auth_session_timer

    def issue_access_token(self, auth_session_id: str) -> str:
        to_encode: dict[str, Any] = {
            "auth_session_id": auth_session_id,
            "exp": int(self._utc_auth_session_timer.access_expiration.timestamp()),
        }

        return jwt.encode(
            payload=to_encode,
            key=self._secret,
            algorithm=self._algorithm,
        )

    def extract_auth_session_id(self, access_token: str) -> str | None:
        payload: dict[str, Any] | None = self._decode_token(access_token)
        if payload is None:
            log.debug("Empty payload in token.")
            return None

        auth_session_id: str | None = payload.get("auth_session_id")
        if auth_session_id is None:
            log.debug("Token has no auth session id.")
            return None

        return auth_session_id

    def _decode_token(self, token: str) -> dict[str, Any] | None:
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
            log.debug("Token is invalid or expired. Error: %s", error)
            return None
