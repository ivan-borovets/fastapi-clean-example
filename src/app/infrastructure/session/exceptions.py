from app.infrastructure.base.exceptions import InfrastructureError


class AuthenticationError(InfrastructureError):
    pass


class AlreadyAuthenticatedError(InfrastructureError):
    pass
