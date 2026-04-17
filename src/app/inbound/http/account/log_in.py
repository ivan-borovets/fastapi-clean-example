from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter

from app.core.common.authorization.exceptions import AuthorizationError
from app.core.common.exceptions import BusinessTypeError
from app.inbound.http.errors.callbacks import log_info
from app.inbound.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE
from app.outbound.adapters.exceptions import PasswordHasherBusyError
from app.outbound.auth_ctx.exceptions import AlreadyAuthenticatedError, AuthenticationError
from app.outbound.auth_ctx.handlers.log_in import LogIn, LogInRequest
from app.outbound.exceptions import StorageError


def make_log_in_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/login/",
        error_map={
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            AlreadyAuthenticatedError: status.HTTP_403_FORBIDDEN,
            BusinessTypeError: status.HTTP_400_BAD_REQUEST,
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            PasswordHasherBusyError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        description=getdoc(LogIn),
    )
    @inject
    async def log_in(
        request: LogInRequest,
        handler: FromDishka[LogIn],
    ) -> None:
        await handler.execute(request)

    return router
