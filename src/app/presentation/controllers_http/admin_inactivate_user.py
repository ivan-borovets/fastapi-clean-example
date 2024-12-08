from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.user.scenarios.admin_inactivate_user.interactor import (
    InactivateUserInteractor,
)
from app.application.user.scenarios.admin_inactivate_user.payload import (
    InactivateUserRequest,
    InactivateUserResponse,
)
from app.presentation.dependencies import cookie_scheme
from app.presentation.exception_handler import ExceptionSchema
from app.setup.ioc.enum_component import ComponentEnum

inactivate_user_router = APIRouter()


@inactivate_user_router.patch(
    "/inactivate",
    responses={
        status.HTTP_200_OK: {"model": InactivateUserResponse},
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
async def inactivate_user(
    request_data: InactivateUserRequest,
    interactor: Annotated[
        InactivateUserInteractor,
        FromComponent(ComponentEnum.USER),
    ],
) -> InactivateUserResponse:
    # :raises AuthenticationError 401:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises DataGatewayError 500:
    # :raises UserNotFoundByUsername 404:
    return await interactor(request_data)
