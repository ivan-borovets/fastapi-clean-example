from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status

from app.application.commands.inactivate_user import (
    InactivateUserInteractor,
    InactivateUserRequest,
)
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.exceptions.schemas import (
    ExceptionSchema,
    ExceptionSchemaDetailed,
)

inactivate_user_router = APIRouter()


@inactivate_user_router.patch(
    "/inactivate",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaDetailed},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def inactivate_user(
    request_data: InactivateUserRequest,
    interactor: FromDishka[InactivateUserInteractor],
) -> None:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 503:
    # :raises AuthorizationError 403:
    # :raises DomainFieldError 400:
    # :raises UserNotFoundByUsername 404:
    # :raises ActivationChangeNotPermitted 403:
    await interactor(request_data)
