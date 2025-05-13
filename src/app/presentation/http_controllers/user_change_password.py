from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.commands.user_change_password import (
    ChangePasswordInteractor,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from app.presentation.common.exception_handler import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.presentation.common.fastapi_dependencies import cookie_scheme

change_password_router = APIRouter()


@change_password_router.patch(
    "/change-password",
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
async def change_password(
    request_data: ChangePasswordRequest,
    interactor: FromDishka[ChangePasswordInteractor],
) -> ChangePasswordResponse:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 500:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    return await interactor(request_data)
