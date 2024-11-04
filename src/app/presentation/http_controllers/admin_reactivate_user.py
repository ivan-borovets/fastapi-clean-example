from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.commands.admin_reactivate_user import (
    ReactivateUserInteractor,
    ReactivateUserRequest,
    ReactivateUserResponse,
)
from app.presentation.common.exception_handler import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.presentation.common.fastapi_dependencies import cookie_scheme
from app.setup.ioc.di_component_enum import ComponentEnum

reactivate_user_router = APIRouter()


@reactivate_user_router.patch(
    "/reactivate",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def reactivate_user(
    request_data: ReactivateUserRequest,
    interactor: Annotated[
        ReactivateUserInteractor,
        FromComponent(ComponentEnum.USER),
    ],
) -> ReactivateUserResponse:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 500:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    return await interactor(request_data)
