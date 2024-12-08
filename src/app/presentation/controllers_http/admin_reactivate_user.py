from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.user.scenarios.admin_reactivate_user.interactor import (
    ReactivateUserInteractor,
)
from app.application.user.scenarios.admin_reactivate_user.payload import (
    ReactivateUserRequest,
    ReactivateUserResponse,
)
from app.presentation.dependencies import cookie_scheme
from app.presentation.exception_handler import ExceptionSchema
from app.setup.ioc.enum_component import ComponentEnum

reactivate_user_router = APIRouter()


@reactivate_user_router.patch(
    "/reactivate",
    responses={
        status.HTTP_200_OK: {"model": ReactivateUserResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
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
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises DataGatewayError 500:
    # :raises UserNotFoundByUsername 404:
    return await interactor(request_data)
