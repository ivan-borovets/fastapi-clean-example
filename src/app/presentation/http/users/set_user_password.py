from inspect import getdoc
from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path
from fastapi_error_map import ErrorAwareRouter
from pydantic import BaseModel, ConfigDict
from starlette import status

from app.core.commands.exceptions import UserNotFoundError
from app.core.commands.set_user_password import SetUserPassword, SetUserPasswordRequest
from app.core.common.authorization.exceptions import AuthorizationError
from app.core.common.exceptions import BusinessTypeError
from app.outbound.adapters.exceptions import PasswordHasherBusyError
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.exceptions import StorageError
from app.presentation.http.errors.callbacks import log_info
from app.presentation.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE


class SetUserPasswordRequestSchema(BaseModel):
    """
    Using Pydantic model here is generally unnecessary.
    It's only implemented to render specific Swagger UI.
    """

    model_config = ConfigDict(frozen=True)

    password: str


def make_set_user_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{user_id}/password/",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            BusinessTypeError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundError: status.HTTP_404_NOT_FOUND,
            PasswordHasherBusyError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        description=getdoc(SetUserPassword),
    )
    @inject
    async def set_user_password(
        user_id: Annotated[UUID, Path()],
        request_schema: SetUserPasswordRequestSchema,
        interactor: FromDishka[SetUserPassword],
    ) -> None:
        request = SetUserPasswordRequest(
            user_id=user_id,
            password=request_schema.password,
        )
        await interactor.execute(request)

    return router
