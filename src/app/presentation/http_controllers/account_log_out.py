from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.infrastructure.auth_context.log_out import LogOutHandler, LogOutResponse
from app.presentation.common.exception_handler import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.presentation.common.fastapi_dependencies import cookie_scheme
from app.setup.ioc.di_component_enum import ComponentEnum

log_out_router = APIRouter()


@log_out_router.delete(
    "/logout",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def logout(
    interactor: Annotated[
        LogOutHandler,
        FromComponent(ComponentEnum.AUTH),
    ],
) -> LogOutResponse:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 500:
    return await interactor()
