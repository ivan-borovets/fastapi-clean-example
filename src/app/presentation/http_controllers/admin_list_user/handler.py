from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status

from app.application.admin_list_users import (
    ListUsersInteractor,
    ListUsersRequest,
    ListUsersResponse,
)
from app.presentation.common.exception_handler import ExceptionSchema
from app.presentation.common.fastapi_dependencies import cookie_scheme
from app.presentation.http_controllers.admin_list_user.pydantic_schema import (
    ListUsersRequestPydantic,
)
from app.setup.ioc.di_component_enum import ComponentEnum

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
    # :raises DataMapperError 500:
    # :raises AuthorizationError 403:
    request_data: ListUsersRequest = ListUsersRequest(
        limit=request_data_pydantic.limit,
        offset=request_data_pydantic.offset,
    )
    return await interactor(request_data)
