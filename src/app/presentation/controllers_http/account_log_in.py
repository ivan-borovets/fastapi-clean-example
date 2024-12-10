from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.infrastructure.session.scenarios.log_in.interactor import LogInInteractor
from app.infrastructure.session.scenarios.log_in.payload import (
    LogInRequest,
    LogInResponse,
)
from app.presentation.exception_handler import ExceptionSchema
from app.setup.ioc.enum_component import ComponentEnum

log_in_router = APIRouter()


@log_in_router.post(
    "/login",
    responses={
        status.HTTP_200_OK: {"model": LogInResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def login(
    request_data: LogInRequest,
    interactor: Annotated[
        LogInInteractor,
        FromComponent(ComponentEnum.SESSION),
    ],
) -> LogInResponse:
    # :raises AlreadyAuthenticatedError 401:
    # :raises DataMapperError 500:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    return await interactor(request_data)
