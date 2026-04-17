from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, status
from fastapi_error_map import ErrorAwareRouter

from app.core.commands.deactivate_user import DeactivateUser, DeactivateUserRequest
from app.core.commands.exceptions import UserNotFoundError
from app.core.common.authorization.exceptions import AuthorizationError
from app.inbound.http.errors.callbacks import log_info
from app.inbound.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.exceptions import StorageError


def make_deactivate_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{user_id}/activation/",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            UserNotFoundError: status.HTTP_404_NOT_FOUND,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        description=getdoc(DeactivateUser),
    )
    @inject
    async def deactivate_user(
        user_id: Annotated[UUID, Path()],
        interactor: FromDishka[DeactivateUser],
    ) -> None:
        request = DeactivateUserRequest(user_id)
        await interactor.execute(request)

    return router
