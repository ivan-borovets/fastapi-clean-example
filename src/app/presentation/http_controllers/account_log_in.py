from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.infrastructure.auth_context.log_in import LogInHandler, LogInRequest
from app.presentation.common.exception_handler import (
    ExceptionSchema,
    ExceptionSchemaRich,
)

log_in_router = APIRouter()


@log_in_router.post(
    "/login",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def login(
    request_data: LogInRequest,
    interactor: FromDishka[LogInHandler],
) -> None:
    # :raises AlreadyAuthenticatedError 401:
    # :raises DataMapperError 500:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    await interactor(request_data)
