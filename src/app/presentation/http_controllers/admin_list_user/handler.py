from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status

from app.application.user_scenarios.admin_list_users.interactor import (
    ListUsersInteractor,
)
from app.application.user_scenarios.admin_list_users.payload import (
    ListUsersRequest,
    ListUsersResponse,
)
from app.presentation.dependencies import cookie_scheme
from app.presentation.exception_handler import ExceptionSchema
from app.presentation.http_controllers.admin_list_user.schemas import (
    ListUsersRequestPydantic,
)
from app.setup.ioc.enum_component import ComponentEnum

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
    dependencies=[Security(cookie_scheme)],
)
@inject
async def list_users(
    request_data_pydantic: Annotated[ListUsersRequestPydantic, Depends()],
    interactor: Annotated[
        ListUsersInteractor,
        FromComponent(ComponentEnum.USER),
    ],
) -> ListUsersResponse:
    # :raises AuthenticationError 401:
    # :raises AuthorizationError 403:
    # :raises DataGatewayError 500:
    request_data: ListUsersRequest = ListUsersRequest(
        limit=request_data_pydantic.limit,
        offset=request_data_pydantic.offset,
    )
    return await interactor(request_data)
