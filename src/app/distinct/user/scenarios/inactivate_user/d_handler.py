from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.common.d_presentation.http_controllers.dependencies import cookie_scheme
from app.common.d_presentation.http_controllers.exception_handler import ExceptionSchema
from app.distinct.user.scenarios.inactivate_user.b_interactor import (
    InactivateUserInteractor,
)
from app.distinct.user.scenarios.inactivate_user.b_payload import (
    InactivateUserRequest,
    InactivateUserResponse,
)
from app.distinct.user.scenarios.inactivate_user.d_request_schema import (
    InactivateUserRequestPydantic,
)

inactivate_user_router = APIRouter()


@inactivate_user_router.patch(
    "/inactivate",
    responses={
        status.HTTP_200_OK: {"model": InactivateUserResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def inactivate_user(
    request_data_pydantic: InactivateUserRequestPydantic,
    interactor: FromDishka[InactivateUserInteractor],
    _token_marker: str = Security(cookie_scheme),
) -> InactivateUserResponse:
    # :raises AuthenticationError:
    # :raises AuthorizationError:
    # :raises UserNotFoundByUsername:
    # :raises GatewayError:
    request_data: InactivateUserRequest = InactivateUserRequest(
        **request_data_pydantic.model_dump()
    )
    return await interactor(request_data)
