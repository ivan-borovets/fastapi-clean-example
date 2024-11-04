from app.infrastructure.base.exceptions import InfrastructureError


class SessionNotFoundById(InfrastructureError):
    def __init__(self, session_id: str):
        message: str = f"Session with id '{session_id}' is not found."
        super().__init__(message)


class SessionExpired(InfrastructureError):
    def __init__(self, session_id: str):
        message: str = f"Session with id '{session_id}' is expired or revoked."
        super().__init__(message)
