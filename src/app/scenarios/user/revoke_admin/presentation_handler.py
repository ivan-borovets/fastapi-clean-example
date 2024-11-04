from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.presentation.http_controllers.dependencies import cookie_scheme
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.user.revoke_admin.application_interactor import RevokeAdminInteractor
from app.scenarios.user.revoke_admin.application_payload import (
    RevokeAdminRequest,
    RevokeAdminResponse,
)
from app.scenarios.user.revoke_admin.presentation_schemas import (
    RevokeAdminRequestPydantic,
)

revoke_admin_router = APIRouter()


@revoke_admin_router.patch(
    "/revoke",
    responses={
        status.HTTP_200_OK: {"model": RevokeAdminResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def revoke_admin(
    request_data_pydantic: RevokeAdminRequestPydantic,
    interactor: FromDishka[RevokeAdminInteractor],
    _token_marker: str = Security(cookie_scheme),
) -> RevokeAdminResponse:
    # :raises AuthenticationError:
    # :raises AuthorizationError:
    # :raises DataGatewayError:
    # :raises UserNotFoundByUsername:
    request_data: RevokeAdminRequest = RevokeAdminRequest(
        request_data_pydantic.username,
    )
    return await interactor(request_data)
