from app.base.b_application.exceptions import ApplicationError


class AdapterError(ApplicationError):
    pass


class GatewayError(ApplicationError):
    pass
