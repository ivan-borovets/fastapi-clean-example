from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.commands.admin_create_user import (
    CreateUserInteractor,
    CreateUserRequest,
    CreateUserResponse,
)
from app.presentation.common.exception_handler import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.presentation.common.fastapi_dependencies import cookie_scheme
from app.presentation.http_controllers.admin_create_user.pydantic_schema import (
    CreateUserRequestPydantic,
)

create_user_router = APIRouter()


@create_user_router.post(
    "/",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def create_user(
    request_data_pydantic: CreateUserRequestPydantic,
    interactor: FromDishka[CreateUserInteractor],
) -> CreateUserResponse:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 500:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises UsernameAlreadyExists 409:
    request_data = CreateUserRequest(
        username=request_data_pydantic.username,
        password=request_data_pydantic.password,
        role=request_data_pydantic.role,
    )
    return await interactor(request_data)
