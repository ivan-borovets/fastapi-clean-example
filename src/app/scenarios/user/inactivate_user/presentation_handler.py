from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.presentation.http_controllers.dependencies import cookie_scheme
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.user.inactivate_user.application_interactor import (
    InactivateUserInteractor,
)
from app.scenarios.user.inactivate_user.application_payload import (
    InactivateUserRequest,
    InactivateUserResponse,
)
from app.scenarios.user.inactivate_user.presentation_schemas import (
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
    # :raises DataGatewayError:
    # :raises UserNotFoundByUsername:
    request_data: InactivateUserRequest = InactivateUserRequest(
        username=request_data_pydantic.username,
    )
    return await interactor(request_data)
