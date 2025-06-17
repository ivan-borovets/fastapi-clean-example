from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from pydantic import BaseModel, ConfigDict, Field

from app.application.commands.create_user import (
    CreateUserInteractor,
    CreateUserRequest,
    CreateUserResponse,
)
from app.domain.enums.user_role import UserRole
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.exceptions.schemas import (
    ExceptionSchema,
    ExceptionSchemaDetailed,
)

create_user_router = APIRouter()


class CreateUserRequestPydantic(BaseModel):
    """
    Using a Pydantic model here is generally unnecessary.
    It's only implemented to render a specific Swagger UI (OpenAPI) schema.
    """

    model_config = ConfigDict(frozen=True)

    username: str
    password: str
    role: UserRole = Field(default=UserRole.USER)


@create_user_router.post(
    "/",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaDetailed},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
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
    # :raises DataMapperError 503:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises UsernameAlreadyExists 409:
    request_data = CreateUserRequest(
        username=request_data_pydantic.username,
        password=request_data_pydantic.password,
        role=request_data_pydantic.role,
    )
    return await interactor(request_data)
