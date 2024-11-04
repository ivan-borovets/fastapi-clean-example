from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.presentation.http_controllers.dependencies import cookie_scheme
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.user.create_user.application_interactor import CreateUserInteractor
from app.scenarios.user.create_user.application_payload import (
    CreateUserRequest,
    CreateUserResponse,
)
from app.scenarios.user.create_user.presentation_schemas import (
    CreateUserRequestPydantic,
)

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
)
@inject
async def create_user(
    request_data_pydantic: CreateUserRequestPydantic,
    interactor: FromDishka[CreateUserInteractor],
    _token_marker: str = Security(cookie_scheme),
) -> CreateUserResponse:
    # :raises AuthenticationError:
    # :raises AuthorizationError:
    # :raises DataGatewayError:
    # :raises UsernameAlreadyExists:
    request_data: CreateUserRequest = CreateUserRequest(
        username=request_data_pydantic.username,
        password=request_data_pydantic.password,
        roles=request_data_pydantic.roles,
    )
    return await interactor(request_data)
