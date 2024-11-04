from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.common.d_presentation.http_controllers.exception_handler import ExceptionSchema
from app.distinct.user.scenarios.sign_up.b_interactor import SignUpInteractor
from app.distinct.user.scenarios.sign_up.b_payload import SignUpRequest, SignUpResponse
from app.distinct.user.scenarios.sign_up.d_request_schema import SignUpRequestPydantic

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
    interactor: FromDishka[SignUpInteractor],
) -> SignUpResponse:
    # :raises GatewayError:
    # :raises UsernameAlreadyExists:
    request_data: SignUpRequest = SignUpRequest(**request_data_pydantic.model_dump())
    return await interactor(request_data)
