from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status

from app.application.commands.grant_admin import (
    GrantAdminInteractor,
    GrantAdminRequest,
)
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.exceptions.schemas import (
    ExceptionSchema,
    ExceptionSchemaDetailed,
)

grant_admin_router = APIRouter()


@grant_admin_router.patch(
    "/{username}/grant-admin",
    description=getdoc(GrantAdminInteractor),
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
    dependencies=[Security(cookie_scheme)],
)
@inject
async def grant_admin(
    username: Annotated[str, Path()],
    interactor: FromDishka[GrantAdminInteractor],
) -> None:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 503:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    # :raises RoleChangeNotPermitted 403:
    request_data = GrantAdminRequest(username)
    await interactor.execute(request_data)
