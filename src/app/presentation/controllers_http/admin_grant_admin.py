from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.user.scenarios.admin_grant_admin.interactor import (
    GrantAdminInteractor,
)
from app.application.user.scenarios.admin_grant_admin.payload import (
    GrantAdminRequest,
    GrantAdminResponse,
)
from app.presentation.dependencies import cookie_scheme
from app.presentation.exception_handler import ExceptionSchema
from app.setup.ioc.enum_component import ComponentEnum

grant_admin_router = APIRouter()


@grant_admin_router.patch(
    "/grant",
    responses={
        status.HTTP_200_OK: {"model": GrantAdminResponse},
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
async def grant_admin(
    request_data: GrantAdminRequest,
    interactor: Annotated[
        GrantAdminInteractor,
        FromComponent(ComponentEnum.USER),
    ],
) -> GrantAdminResponse:
    # :raises AuthenticationError 401:
    # :raises AuthorizationError 403:
    # :raises DataMapperError 500:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    return await interactor(request_data)
