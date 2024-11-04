from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.common.d_presentation.http_controllers.exception_handler import ExceptionSchema
from app.distinct.user.scenarios.log_in.b_interactor import LogInInteractor
from app.distinct.user.scenarios.log_in.b_payload import LogInRequest, LogInResponse
from app.distinct.user.scenarios.log_in.d_request_schema import LogInRequestPydantic

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
    interactor: FromDishka[LogInInteractor],
) -> LogInResponse:
    # :raises AuthenticationError:
    # :raises UserNotFoundByUsername:
    # :raises GatewayError:
    request_data: LogInRequest = LogInRequest(**request_data_pydantic.model_dump())
    return await interactor(request_data)
