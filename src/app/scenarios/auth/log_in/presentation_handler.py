from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.application.user.services.account import AccountService
from app.domain.user.vo_user import Username
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.auth.log_in.presentation_schemas import (
    LogInRequestPydantic,
    LogInResponse,
)

log_in_router = APIRouter()


@log_in_router.post(
    "/login",
    responses={
        status.HTTP_200_OK: {"model": LogInResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def login(
    request_data_pydantic: LogInRequestPydantic,
    account_service: FromDishka[AccountService],
) -> LogInResponse:
    # :raises AuthenticationError:
    # :raises DataGatewayError:
    # :raises UserNotFoundByUsername:
    username: str = request_data_pydantic.username
    password: str = request_data_pydantic.password
    await account_service.log_in(Username(username), password)
    return LogInResponse("Successfully logged in.")
