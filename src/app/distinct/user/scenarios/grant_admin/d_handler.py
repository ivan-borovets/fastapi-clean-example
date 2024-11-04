from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.common.d_presentation.http_controllers.dependencies import cookie_scheme
from app.common.d_presentation.http_controllers.exception_handler import ExceptionSchema
from app.distinct.user.scenarios.grant_admin.b_interactor import GrantAdminInteractor
from app.distinct.user.scenarios.grant_admin.b_payload import (
    GrantAdminRequest,
    GrantAdminResponse,
)
from app.distinct.user.scenarios.grant_admin.d_request_schema import (
    GrantAdminRequestPydantic,
)

grant_admin_router = APIRouter()


@grant_admin_router.patch(
    "/grant",
    responses={
        status.HTTP_200_OK: {"model": GrantAdminResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def grant_admin(
    request_data_pydantic: GrantAdminRequestPydantic,
    interactor: FromDishka[GrantAdminInteractor],
    _token_marker: str = Security(cookie_scheme),
) -> GrantAdminResponse:
    # :raises AuthenticationError:
    # :raises AuthorizationError:
    # :raises UserNotFoundByUsername:
    # :raises GatewayError:
    request_data: GrantAdminRequest = GrantAdminRequest(
        **request_data_pydantic.model_dump()
    )
    return await interactor(request_data)
