from typing import Any

from app.application.base.exceptions import ApplicationError


class AuthenticationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    pass


class SessionExpired(ApplicationError):
    def __init__(self, session_id: Any):
        message: str = f"Session with id '{session_id}' is expired or revoked."
        super().__init__(message)
