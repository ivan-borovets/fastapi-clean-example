from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.user.scenarios.admin_create_user.interactor import (
    CreateUserInteractor,
)
from app.application.user.scenarios.admin_create_user.payload import (
    CreateUserRequest,
    CreateUserResponse,
)
from app.presentation.dependencies import cookie_scheme
from app.presentation.exception_handler import ExceptionSchema
from app.setup.ioc.enum_component import ComponentEnum

create_user_router = APIRouter()


@create_user_router.post(
    "/",
    responses={
        status.HTTP_201_CREATED: {"model": CreateUserResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def create_user(
    request_data: CreateUserRequest,
    interactor: Annotated[
        CreateUserInteractor,
        FromComponent(ComponentEnum.USER),
    ],
) -> CreateUserResponse:
    # :raises AuthenticationError 401:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises DataGatewayError 500:
    # :raises UsernameAlreadyExists 409:
    return await interactor(request_data)
