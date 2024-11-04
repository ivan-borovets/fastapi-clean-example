from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.application.enums import ResponseStatusEnum
from app.application.user.services.account import AccountService
from app.domain.user.vo_user import Username
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.auth.sign_up.presentation_schemas import (
    SignUpRequestPydantic,
    SignUpResponse,
)

sign_up_router = APIRouter()


@sign_up_router.post(
    "/signup",
    responses={
        status.HTTP_201_CREATED: {"model": SignUpResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
)
@inject
async def sign_up(
    request_data_pydantic: SignUpRequestPydantic,
    account_service: FromDishka[AccountService],
) -> SignUpResponse:
    # :raises AuthenticationError:
    # :raises DataGatewayError:
    # :raises UsernameAlreadyExists:
    username: str = request_data_pydantic.username
    password: str = request_data_pydantic.password
    await account_service.sign_up(Username(username), password)
    return SignUpResponse(username, ResponseStatusEnum.CREATED)
