from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.base import DomainFieldError
from app.domain.exceptions.user import (
    RoleAssignmentNotPermittedError,
    UsernameAlreadyExistsError,
)
from app.infrastructure.auth.exceptions import AlreadyAuthenticatedError
from app.infrastructure.auth.handlers.sign_up import (
    SignUpHandler,
    SignUpRequest,
    SignUpResponse,
)
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.errors.callbacks import (
    log_error,
    log_info,
)
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


def create_sign_up_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/signup",
        description=getdoc(SignUpHandler),
        error_map={
            AlreadyAuthenticatedError: status.HTTP_403_FORBIDDEN,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            RoleAssignmentNotPermittedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
    )
    @inject
    async def sign_up(
        request_data: SignUpRequest,
        handler: FromDishka[SignUpHandler],
    ) -> SignUpResponse:
        return await handler.execute(request_data)

    return router
