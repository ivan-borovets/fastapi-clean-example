from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.activate_user import (
    ActivateUserInteractor,
    ActivateUserRequest,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.user import (
    ActivationChangeNotPermittedError,
    UserNotFoundByIdError,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


def create_activate_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{user_id}/activation",
        description=getdoc(ActivateUserInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            ActivationChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def activate_user(
        user_id: Annotated[UUID, Path()],
        interactor: FromDishka[ActivateUserInteractor],
    ) -> None:
        request_data = ActivateUserRequest(user_id)
        await interactor.execute(request_data)

    return router
