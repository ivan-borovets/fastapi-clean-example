from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.user.scenarios.admin_revoke_admin.interactor import (
    RevokeAdminInteractor,
)
from app.application.user.scenarios.admin_revoke_admin.payload import (
    RevokeAdminRequest,
    RevokeAdminResponse,
)
from app.presentation.dependencies import cookie_scheme
from app.presentation.exception_handler import ExceptionSchema
from app.setup.ioc.enum_component import ComponentEnum

revoke_admin_router = APIRouter()


@revoke_admin_router.patch(
    "/revoke",
    responses={
        status.HTTP_200_OK: {"model": RevokeAdminResponse},
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
async def revoke_admin(
    request_data: RevokeAdminRequest,
    interactor: Annotated[
        RevokeAdminInteractor,
        FromComponent(ComponentEnum.USER),
    ],
) -> RevokeAdminResponse:
    # :raises AuthenticationError 401:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises DataGatewayError 500:
    # :raises UserNotFoundByUsername 404:
    return await interactor(request_data)
