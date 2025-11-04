from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from app.application.commands.create_user import (
    CreateUserInteractor,
    CreateUserRequest,
    CreateUserResponse,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.base import DomainTypeError
from app.domain.exceptions.user import (
    RoleAssignmentNotPermittedError,
    UsernameAlreadyExistsError,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.infrastructure.exceptions.password_hasher import PasswordHasherBusyError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


class CreateUserRequestPydantic(BaseModel):
    """
    Using a Pydantic model here is generally unnecessary.
    It's only implemented to render a specific Swagger UI (OpenAPI) schema.
    """

    model_config = ConfigDict(frozen=True)

    username: str
    password: str
    role: UserRole = Field(default=UserRole.USER)


def create_create_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreateUserInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainTypeError: status.HTTP_400_BAD_REQUEST,
            PasswordHasherBusyError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            RoleAssignmentNotPermittedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def create_user(
        request_data_pydantic: CreateUserRequestPydantic,
        interactor: FromDishka[CreateUserInteractor],
    ) -> CreateUserResponse:
        request_data = CreateUserRequest(
            username=request_data_pydantic.username,
            password=request_data_pydantic.password,
            role=request_data_pydantic.role,
        )
        return await interactor.execute(request_data)

    return router
