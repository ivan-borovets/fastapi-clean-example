import logging

from app.infrastructure.auth_context.common.jwt_access_token_processor import (
    JwtAccessTokenProcessor,
)
from app.infrastructure.auth_context.common.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)

log = logging.getLogger(__name__)


class JwtTokenManager:
    def __init__(
        self,
        jwt_access_token_processor: JwtAccessTokenProcessor,
        access_token_request_handler: AccessTokenRequestHandler,
    ):
        self._jwt_access_token_processor = jwt_access_token_processor
        self._access_token_request_handler = access_token_request_handler

    def issue_access_token(self, auth_session_id: str) -> str:
        log.debug(
            "Issue access token: started. Auth session id: '%s'.",
            auth_session_id,
        )

        access_token: str = self._jwt_access_token_processor.issue_access_token(
            auth_session_id,
        )

        log.debug("Issue access token: done. Auth session id: '%s'.", auth_session_id)
        return access_token

    def add_access_token_to_request(self, access_token: str) -> None:
        log.debug("Add access token to request: started.")

        self._access_token_request_handler.add_access_token_to_request(access_token)

        log.debug("Add access token to request: done.")

    def delete_access_token_from_request(self) -> None:
        log.debug("Delete access token from request: started.")

        self._access_token_request_handler.delete_access_token_from_request()

        log.debug("Delete access token from request: done.")

    def get_access_token_from_request(self) -> str | None:
        log.debug("Get access token from request: started.")

        access_token: str | None = (
            self._access_token_request_handler.get_access_token_from_request()
        )
        if not access_token:
            log.debug(
                "Get access token from request: done. No access token in request.",
            )
            return None

        log.debug("Get access token from request: done.")
        return access_token

    def get_auth_session_id_from_access_token(self, access_token: str) -> str | None:
        log.debug("Get auth session id from access token: started.")

        auth_session_id: str | None = (
            self._jwt_access_token_processor.extract_auth_session_id(access_token)
        )
        if auth_session_id is None:
            log.debug(
                "Get auth session id from access token: failed. No auth session id.",
            )
            return None

        log.debug("Get auth session id from access token: done.")
        return auth_session_id
