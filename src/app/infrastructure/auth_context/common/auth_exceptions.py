from app.infrastructure.exceptions.base import InfrastructureError


class AuthenticationError(InfrastructureError):
    pass


class AlreadyAuthenticatedError(InfrastructureError):
    pass
