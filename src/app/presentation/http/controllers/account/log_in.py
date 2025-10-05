from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.base import DomainTypeError
from app.domain.exceptions.user import UserNotFoundByUsernameError
from app.infrastructure.auth.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.auth.handlers.log_in import LogInHandler, LogInRequest
from app.infrastructure.exceptions.gateway import DataMapperError
from app.infrastructure.exceptions.password_hasher import PasswordHasherBusyError
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


def create_log_in_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/login",
        description=getdoc(LogInHandler),
        error_map={
            AlreadyAuthenticatedError: status.HTTP_403_FORBIDDEN,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundByUsernameError: status.HTTP_404_NOT_FOUND,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def login(
        request_data: LogInRequest,
        handler: FromDishka[LogInHandler],
    ) -> None:
        await handler.execute(request_data)

    return router
