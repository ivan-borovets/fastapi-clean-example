from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, status
from fastapi.security import APIKeyCookie
from fastapi_error_map import ErrorAwareRouter

from app.core.common.authorization.exceptions import AuthorizationError
from app.infrastructure.auth_ctx.exceptions import AuthenticationError
from app.infrastructure.auth_ctx.handlers.log_out import LogOut
from app.infrastructure.exceptions import StorageError
from app.presentation.http.errors.callbacks import log_info
from app.presentation.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE


def make_log_out_router(*, cookie_name: str) -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/logout/",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(APIKeyCookie(name=cookie_name))],
        description=getdoc(LogOut),
    )
    @inject
    async def log_out(handler: FromDishka[LogOut]) -> None:
        await handler.execute()

    return router
