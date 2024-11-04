from typing import Any

from app.base.a_domain.exceptions import DomainError


class SessionExpired(DomainError):
    def __init__(self, session_id: Any):
        message: str = f"Session with id '{session_id}' is expired or revoked."
        super().__init__(message)
