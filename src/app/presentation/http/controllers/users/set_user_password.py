from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.set_user_password import (
    SetUserPasswordInteractor,
    SetUserPasswordRequest,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.base import DomainTypeError
from app.domain.exceptions.user import (
    UserNotFoundByIdError,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.infrastructure.exceptions.password_hasher import PasswordHasherBusyError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


def create_set_user_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{user_id}/password",
        description=getdoc(SetUserPasswordInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def set_user_password(
        user_id: Annotated[UUID, Path()],
        password: Annotated[str, Body()],
        interactor: FromDishka[SetUserPasswordInteractor],
    ) -> None:
        request_data = SetUserPasswordRequest(
            user_id=user_id,
            password=password,
        )
        await interactor.execute(request_data)

    return router
