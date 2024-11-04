from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.presentation.http_controllers.dependencies import cookie_scheme
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.user.reactivate_user.application_interactor import (
    ReactivateUserInteractor,
)
from app.scenarios.user.reactivate_user.application_payload import (
    ReactivateUserRequest,
    ReactivateUserResponse,
)
from app.scenarios.user.reactivate_user.presentation_schemas import (
    ReactivateUserRequestPydantic,
)

reactivate_user_router = APIRouter()


@reactivate_user_router.patch(
    "/reactivate",
    responses={
        status.HTTP_200_OK: {"model": ReactivateUserResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def reactivate_user(
    request_data_pydantic: ReactivateUserRequestPydantic,
    interactor: FromDishka[ReactivateUserInteractor],
    _token_marker: str = Security(cookie_scheme),
) -> ReactivateUserResponse:
    # :raises AuthenticationError:
    # :raises AuthorizationError:
    # :raises DataGatewayError:
    # :raises UserNotFoundByUsername:
    request_data: ReactivateUserRequest = ReactivateUserRequest(
        username=request_data_pydantic.username
    )
    return await interactor(request_data)
