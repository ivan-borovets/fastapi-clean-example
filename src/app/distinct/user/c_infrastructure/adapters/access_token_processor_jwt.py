from typing import Any, cast

import jwt

from app.common.b_application.exceptions import AdapterError
from app.common.c_infrastructure.custom_types import JwtAlgorithm, JwtSecret
from app.distinct.user.a_domain.vo_session import SessionId
from app.distinct.user.b_application.ports.access_token_processor import (
    AccessTokenProcessor,
)
from app.distinct.user.b_application.ports.session_timer import SessionTimer


class JwtAccessTokenProcessor(AccessTokenProcessor):
    def __init__(
        self,
        secret: JwtSecret,
        algorithm: JwtAlgorithm,
        session_timer: SessionTimer,
    ):
        self._secret = secret
        self._algorithm = algorithm
        self._session_timer = session_timer

    def issue_access_token(self, session_id: SessionId) -> str:
        to_encode: dict[str, Any] = {
            "session_id": session_id.value,
            "exp": int(self._session_timer.access_expiration.timestamp()),
        }
        return jwt.encode(
            payload=to_encode,
            key=self._secret,
            algorithm=self._algorithm,
        )

    def extract_session_id(self, access_token: str) -> SessionId:
        """
        :raises AdapterError:
        """
        try:
            payload: dict[str, Any] = self._decode_token(access_token)
        except AdapterError:
            raise

        session_id: str | None = payload.get("session_id")
        if session_id is None:
            raise AdapterError("Token has no Session id.")

        return SessionId(session_id)

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
