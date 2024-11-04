from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.common.d_presentation.http_controllers.dependencies import cookie_scheme
from app.common.d_presentation.http_controllers.exception_handler import ExceptionSchema
from app.distinct.user.scenarios.log_out.b_interactor import LogOutInteractor
from app.distinct.user.scenarios.log_out.b_payload import LogOutResponse

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
    interactor: FromDishka[LogOutInteractor],
    _token_marker: str = Security(cookie_scheme),
) -> LogOutResponse:
    # :raises AuthenticationError:
    return await interactor()
