from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status

from app.presentation.http_controllers.dependencies import cookie_scheme
from app.presentation.http_controllers.exception_handler import ExceptionSchema
from app.scenarios.user.list_users.application_interactor import ListUsersInteractor
from app.scenarios.user.list_users.application_payload import (
    ListUsersRequest,
    ListUsersResponse,
)
from app.scenarios.user.list_users.presentation_schemas import ListUsersRequestPydantic

list_users_router = APIRouter()


@list_users_router.get(
    "/",
    responses={
        status.HTTP_200_OK: {"model": ListUsersResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def list_users(
    request_data_pydantic: Annotated[ListUsersRequestPydantic, Depends()],
    interactor: FromDishka[ListUsersInteractor],
    _token_marker: str = Security(cookie_scheme),
) -> ListUsersResponse:
    # :raises AuthenticationError:
    # :raises AuthorizationError:
    # :raises DataGatewayError:
    request_data: ListUsersRequest = ListUsersRequest(
        limit=request_data_pydantic.limit,
        offset=request_data_pydantic.offset,
    )
    return await interactor(request_data)
