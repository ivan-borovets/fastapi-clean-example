from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.infrastructure.auth.handlers.log_out import LogOutHandler
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.exceptions.schemas import (
    ExceptionSchema,
    ExceptionSchemaDetailed,
)

log_out_router = APIRouter()


@log_out_router.delete(
    "/logout",
    description=getdoc(LogOutHandler),
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaDetailed},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def logout(
    handler: FromDishka[LogOutHandler],
) -> None:
    # :raises AuthenticationError 401:
    # :raises AuthorizationError 403:
    # :raises DataMapperError 503:
    await handler.execute()
