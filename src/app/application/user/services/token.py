import logging

from app.application.user.ports.access_token_processor import AccessTokenProcessor
from app.application.user.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)

log = logging.getLogger(__name__)


class TokenService:
    def __init__(
        self,
        access_token_processor: AccessTokenProcessor,
        access_token_request_handler: AccessTokenRequestHandler,
    ):
        self._access_token_processor = access_token_processor
        self._access_token_request_handler = access_token_request_handler

    def issue_access_token(self, session_id: str) -> str:
        log.debug("Issue access token: started. Session id: '%s'.", session_id)

        access_token: str = self._access_token_processor.issue_access_token(session_id)

        log.debug("Issue access token: done. Session id: '%s'.", session_id)
        return access_token

    def add_access_token_to_request(self, access_token: str) -> None:
        log.debug("Add access token to request: started.")

        self._access_token_request_handler.add_access_token_to_request(access_token)

        log.debug("Add access token to request: done.")

    def delete_access_token_from_request(self) -> None:
        log.debug("Delete access token from request: started.")

        self._access_token_request_handler.delete_access_token_from_request()

        log.debug("Delete access token from request: done.")

    def get_access_token_from_request(self) -> str:
        """
        :raises AdapterError:
        """
        log.debug("Get access token from request: started.")

        access_token: str = (
            self._access_token_request_handler.get_access_token_from_request()
        )

        log.debug("Get access token from request: done.")
        return access_token

    def get_session_id_from_access_token(self, access_token: str) -> str:
        log.debug("Get session id from access token: started.")

        session_id: str = self._access_token_processor.extract_session_id(access_token)

        log.debug("Get session id from access token: done.")
        return session_id
