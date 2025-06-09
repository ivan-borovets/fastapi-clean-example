from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.commands.grant_admin import (
    GrantAdminInteractor,
    GrantAdminRequest,
)
from app.presentation.web.exception_handlers import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.presentation.web.fastapi_openapi_markers import cookie_scheme

grant_admin_router = APIRouter()


@grant_admin_router.patch(
    "/grant",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def grant_admin(
    request_data: GrantAdminRequest,
    interactor: FromDishka[GrantAdminInteractor],
) -> None:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 503:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    # :raises RoleChangeNotPermitted 403:
    await interactor(request_data)
