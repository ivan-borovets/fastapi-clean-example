import logging
from typing import Any, Literal, TypedDict, cast

import jwt

from app.infrastructure.auth.session.model import AuthSession
from app.presentation.http.auth.constants import (
    ACCESS_TOKEN_INVALID_OR_EXPIRED,
    ACCESS_TOKEN_PAYLOAD_MISSING,
    ACCESS_TOKEN_PAYLOAD_OF_INTEREST,
)

log = logging.getLogger(__name__)


class JwtPayload(TypedDict):
    auth_session_id: str
    exp: int


class JwtAccessTokenProcessor:
    def __init__(
        self,
        secret: str,
        algorithm: Literal[
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
        ],
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm

    def encode(self, auth_session: AuthSession) -> str:
        payload = JwtPayload(
            auth_session_id=auth_session.id_,
            exp=int(auth_session.expiration.timestamp()),
        )
        return jwt.encode(
            cast(dict[str, Any], payload),
            key=self._secret,
            algorithm=self._algorithm,
        )

    def decode_auth_session_id(self, token: str) -> str | None:
        try:
            payload = jwt.decode(
                token,
                key=self._secret,
                algorithms=[self._algorithm],
            )

        except jwt.PyJWTError as err:
            log.debug("%s %s", ACCESS_TOKEN_INVALID_OR_EXPIRED, err)
            return None

        auth_session_id: str | None = payload.get(ACCESS_TOKEN_PAYLOAD_OF_INTEREST)
        if auth_session_id is None:
            log.debug(
                "%s '%s'",
                ACCESS_TOKEN_PAYLOAD_MISSING,
                ACCESS_TOKEN_PAYLOAD_OF_INTEREST,
            )
            return None

        return auth_session_id
