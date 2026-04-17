from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, status
from fastapi_error_map import ErrorAwareRouter

from app.core.commands.exceptions import UserNotFoundError
from app.core.commands.grant_admin import GrantAdmin, GrantAdminRequest
from app.core.common.authorization.exceptions import AuthorizationError
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.exceptions import StorageError
from app.presentation.http.errors.callbacks import log_info
from app.presentation.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE


def make_grant_admin_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{user_id}/roles/admin/",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            UserNotFoundError: status.HTTP_404_NOT_FOUND,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        description=getdoc(GrantAdmin),
    )
    @inject
    async def grant_admin(
        user_id: Annotated[UUID, Path()],
        interactor: FromDishka[GrantAdmin],
    ) -> None:
        request = GrantAdminRequest(user_id)
        await interactor.execute(request)

    return router
