from app.application.base.exceptions import ApplicationError


class AuthorizationError(ApplicationError):
    pass


class AuthenticationError(ApplicationError):
    pass


class AlreadyAuthenticatedError(ApplicationError):
    pass
