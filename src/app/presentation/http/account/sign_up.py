from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from fastapi_error_map import ErrorAwareRouter

from app.core.commands.exceptions import UsernameAlreadyExistsError
from app.core.common.authorization.exceptions import AuthorizationError
from app.core.common.exceptions import BusinessTypeError
from app.infrastructure.adapters.exceptions import PasswordHasherBusyError
from app.infrastructure.auth_ctx.exceptions import AlreadyAuthenticatedError
from app.infrastructure.auth_ctx.handlers.sign_up import SignUp, SignUpRequest
from app.infrastructure.exceptions import StorageError
from app.presentation.http.errors.callbacks import log_info
from app.presentation.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE


def make_sign_up_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/signup/",
        error_map={
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            AlreadyAuthenticatedError: status.HTTP_403_FORBIDDEN,
            BusinessTypeError: status.HTTP_400_BAD_REQUEST,
            PasswordHasherBusyError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        description=getdoc(SignUp),
    )
    @inject
    async def sign_up(
        request: SignUpRequest,
        handler: FromDishka[SignUp],
    ) -> None:
        await handler.execute(request)

    return router
