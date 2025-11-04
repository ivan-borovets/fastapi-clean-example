from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.deactivate_user import (
    DeactivateUserInteractor,
    DeactivateUserRequest,
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


def create_deactivate_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{user_id}/activation",
        description=getdoc(DeactivateUserInteractor),
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
    async def deactivate_user(
        user_id: Annotated[UUID, Path()],
        interactor: FromDishka[DeactivateUserInteractor],
    ) -> None:
        request_data = DeactivateUserRequest(user_id)
        await interactor.execute(request_data)

    return router
