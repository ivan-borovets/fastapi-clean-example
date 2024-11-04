from app.base.b_application.exceptions import ApplicationError


class AuthenticationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    pass
