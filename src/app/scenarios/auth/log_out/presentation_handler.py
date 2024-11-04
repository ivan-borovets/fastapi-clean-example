from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.user.services.account import AccountService
from app.presentation.http_controllers.dependencies import cookie_scheme
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.auth.log_out.presentation_schemas import LogOutResponse

log_out_router = APIRouter()


@log_out_router.delete(
    "/logout",
    responses={
        status.HTTP_200_OK: {"model": LogOutResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def logout(
    account_service: FromDishka[AccountService],
    _token_marker: str = Security(cookie_scheme),
) -> LogOutResponse:
    # :raises AuthenticationError:
    # :raises DataGatewayError:
    await account_service.log_out()
    return LogOutResponse("Successfully logged out.")
