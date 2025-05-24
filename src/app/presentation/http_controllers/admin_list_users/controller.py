from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status

from app.application.queries.admin_list_users import (
    ListUsersQueryService,
    ListUsersRequest,
    ListUsersResponse,
)
from app.presentation.common.exception_handler import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.presentation.common.fastapi_dependencies import cookie_scheme
from app.presentation.http_controllers.admin_list_users.pydantic_schema import (
    ListUsersRequestPydantic,
)

list_users_router = APIRouter()


@list_users_router.get(
    "/",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
    dependencies=[Security(cookie_scheme)],
)
@inject
async def list_users(
    request_data_pydantic: Annotated[ListUsersRequestPydantic, Depends()],
    interactor: FromDishka[ListUsersQueryService],
) -> ListUsersResponse:
    # :raises AuthenticationError 401:
    # :raises DataMapperError 500:
    # :raises AuthorizationError 403:
    # :raises PaginationError 500:
    # :raises ReaderError 500:
    # :raises SortingError 400:
    request_data = ListUsersRequest(
        limit=request_data_pydantic.limit,
        offset=request_data_pydantic.offset,
        sorting_field=request_data_pydantic.sorting_field,
        sorting_order=request_data_pydantic.sorting_order,
    )
    return await interactor(request_data)
