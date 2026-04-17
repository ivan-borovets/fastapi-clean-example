from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from fastapi_error_map import ErrorAwareRouter
from starlette import status

from app.core.commands.create_user import CreateUser, CreateUserRequest, CreateUserResponse
from app.core.commands.exceptions import (
    UsernameAlreadyExistsError,
)
from app.core.common.authorization.exceptions import AuthorizationError
from app.core.common.exceptions import BusinessTypeError
from app.outbound.adapters.exceptions import PasswordHasherBusyError
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.exceptions import StorageError
from app.presentation.http.errors.callbacks import log_info
from app.presentation.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE


def make_create_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            BusinessTypeError: status.HTTP_400_BAD_REQUEST,
            PasswordHasherBusyError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        description=getdoc(CreateUser),
    )
    @inject
    async def create_user(
        request: CreateUserRequest,
        interactor: FromDishka[CreateUser],
    ) -> CreateUserResponse:
        return await interactor.execute(request)

    return router
