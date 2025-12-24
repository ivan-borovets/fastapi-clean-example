from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.revoke_admin import (
    RevokeAdminInteractor,
    RevokeAdminRequest,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.user import (
    RoleChangeNotPermittedError,
    UserNotFoundByIdError,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


def create_revoke_admin_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{user_id}/roles/admin",
        description=getdoc(RevokeAdminInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            UserNotFoundByIdError: status.HTTP_404_NOT_FOUND,
            RoleChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def revoke_admin(
        user_id: Annotated[UUID, Path()],
        interactor: FromDishka[RevokeAdminInteractor],
    ) -> None:
        request_data = RevokeAdminRequest(user_id)
        await interactor.execute(request_data)

    return router
