from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.infrastructure.auth.handlers.log_in import LogInHandler, LogInRequest
from app.presentation.http.exceptions.schemas import (
    ExceptionSchema,
    ExceptionSchemaDetailed,
)

log_in_router = APIRouter()


@log_in_router.post(
    "/login",
    description=getdoc(LogInHandler),
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaDetailed},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def login(
    request_data: LogInRequest,
    handler: FromDishka[LogInHandler],
) -> None:
    # :raises AlreadyAuthenticatedError 401:
    # :raises AuthorizationError 403:
    # :raises DataMapperError 503:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    await handler.execute(request_data)
