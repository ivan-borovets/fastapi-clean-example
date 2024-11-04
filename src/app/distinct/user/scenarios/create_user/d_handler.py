from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.common.d_presentation.http_controllers.dependencies import cookie_scheme
from app.common.d_presentation.http_controllers.exception_handler import ExceptionSchema
from app.distinct.user.scenarios.create_user.b_interactor import CreateUserInteractor
from app.distinct.user.scenarios.create_user.b_payload import (
    CreateUserRequest,
    CreateUserResponse,
)
from app.distinct.user.scenarios.create_user.d_request_schema import (
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
    # :raises UsernameAlreadyExists:
    # :raises GatewayError:
    request_data: CreateUserRequest = CreateUserRequest(
        **request_data_pydantic.model_dump()
    )
    return await interactor(request_data)
