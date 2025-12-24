from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.exceptions.query import PaginationError, SortingError
from app.application.common.ports.user_query_gateway import ListUsersQM
from app.application.common.query_params.sorting import SortingOrder
from app.application.queries.list_users import (
    ListUsersQueryService,
    ListUsersRequest,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError, ReaderError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


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


def create_list_users_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/",
        description=getdoc(ListUsersQueryService),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            PaginationError: status.HTTP_400_BAD_REQUEST,
            SortingError: status.HTTP_400_BAD_REQUEST,
            ReaderError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def list_users(
        request_data_pydantic: Annotated[ListUsersRequestPydantic, Depends()],
        interactor: FromDishka[ListUsersQueryService],
    ) -> ListUsersQM:
        request_data = ListUsersRequest(
            limit=request_data_pydantic.limit,
            offset=request_data_pydantic.offset,
            sorting_field=request_data_pydantic.sorting_field,
            sorting_order=request_data_pydantic.sorting_order,
        )
        return await interactor.execute(request_data)

    return router
