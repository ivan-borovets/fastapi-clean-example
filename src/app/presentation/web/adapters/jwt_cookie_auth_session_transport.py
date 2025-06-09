import logging

from starlette.requests import Request

from app.infrastructure.auth_session.model import AuthSession
from app.infrastructure.auth_session.ports.transport import AuthSessionTransport
from app.presentation.web.adapters.cookie_params import CookieParams
from app.presentation.web.adapters.jwt_access_token_processor import (
    JwtAccessTokenProcessor,
)
from app.presentation.web.constants import (
    ACCESS_TOKEN_DELIVERED_VIA_COOKIE,
    ACCESS_TOKEN_MARKED_FOR_REMOVAL,
    ACCESS_TOKEN_NOT_FOUND_IN_COOKIE,
    COOKIE_ACCESS_TOKEN_NAME,
    REQUEST_STATE_COOKIE_PARAMS_KEY,
    REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY,
    REQUEST_STATE_NEW_ACCESS_TOKEN_KEY,
)

log = logging.getLogger(__name__)


class JwtCookieAuthSessionTransport(AuthSessionTransport):
    def __init__(
        self,
        request: Request,
        access_token_processor: JwtAccessTokenProcessor,
        cookie_params: CookieParams,
    ):
        self._request = request
        self._access_token_processor = access_token_processor
        self._cookie_params = cookie_params

    def deliver(self, auth_session: AuthSession) -> None:
        access_token = self._access_token_processor.encode(auth_session)
        setattr(self._request.state, REQUEST_STATE_NEW_ACCESS_TOKEN_KEY, access_token)
        setattr(
            self._request.state,
            REQUEST_STATE_COOKIE_PARAMS_KEY,
            self._cookie_params,
        )

        log.debug(
            "%s Session ID: %s",
            ACCESS_TOKEN_DELIVERED_VIA_COOKIE,
            auth_session.id_,
        )

    def extract_id(self) -> str | None:
        access_token = self._request.cookies.get(COOKIE_ACCESS_TOKEN_NAME)
        if access_token is None:
            log.debug("%s", ACCESS_TOKEN_NOT_FOUND_IN_COOKIE)
            return None

        return self._access_token_processor.decode_auth_session_id(access_token)

    def remove_current(self) -> None:
        setattr(self._request.state, REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY, True)

        log.debug("%s", ACCESS_TOKEN_MARKED_FOR_REMOVAL)
