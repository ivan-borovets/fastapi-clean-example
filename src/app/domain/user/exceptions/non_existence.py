from typing import Any

from app.domain.base.exceptions import DomainError


class UserNotFoundById(DomainError):
    def __init__(self, user_id: Any):
        message: str = f"User with id '{user_id}' is not found."
        super().__init__(message)


class UserNotFoundByUsername(DomainError):
    def __init__(self, username: Any):
        message: str = f"User with username '{username}' is not found."
        super().__init__(message)


class SessionNotFoundById(DomainError):
    def __init__(self, session_id: Any):
        message: str = f"Session with id '{session_id}' is not found."
        super().__init__(message)
