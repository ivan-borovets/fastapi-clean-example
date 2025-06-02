from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel, ConfigDict, Field

from app.application.common.query_params.sorting import SortingOrder
from app.application.queries.list_users import (
    ListUsersQueryService,
    ListUsersRequest,
    ListUsersResponse,
)
from app.presentation.web.exception_handlers import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.presentation.web.fastapi_openapi_markers import cookie_scheme

list_users_router = APIRouter()


class ListUsersRequestPydantic(BaseModel):
    """
    Using a Pydantic model here is generally unnecessary.
    It's only implemented to render a specific Swagger UI (OpenAPI) schema.
    """

    model_config = ConfigDict(frozen=True)

    limit: Annotated[int, Field(ge=1)] = 20
    offset: Annotated[int, Field(ge=0)] = 0
    sorting_field: Annotated[str, Field()] = "username"
    sorting_order: Annotated[SortingOrder, Field()] = SortingOrder.ASC


@list_users_router.get(
    "/",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_403_FORBIDDEN: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ExceptionSchema},
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
    # :raises DataMapperError 503:
    # :raises AuthorizationError 403:
    # :raises ReaderError 503:
    # :raises PaginationError 500:
    # :raises SortingError 400:
    request_data = ListUsersRequest(
        limit=request_data_pydantic.limit,
        offset=request_data_pydantic.offset,
        sorting_field=request_data_pydantic.sorting_field,
        sorting_order=request_data_pydantic.sorting_order,
    )
    return await interactor(request_data)
