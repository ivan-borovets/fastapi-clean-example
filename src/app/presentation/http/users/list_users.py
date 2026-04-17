from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends
from fastapi_error_map import ErrorAwareRouter
from pydantic import BaseModel, ConfigDict, Field
from starlette import status

from app.core.common.authorization.exceptions import AuthorizationError
from app.core.queries.list_users import ListUsers, ListUsersRequest, UserSortingField
from app.core.queries.ports.user_reader import ListUsersQm
from app.core.queries.query_support.exceptions import PaginationError
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingOrder
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.exceptions import ReaderError, StorageError
from app.presentation.http.errors.callbacks import log_info
from app.presentation.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE


class ListUsersRequestSchema(BaseModel):
    """
    Using Pydantic model here is generally unnecessary.
    It's only implemented to render specific Swagger UI.
    """

    model_config = ConfigDict(frozen=True)

    limit: Annotated[int, Field(ge=1, le=OffsetPaginationParams.MAX_INT32)] = 20
    offset: Annotated[int, Field(ge=0, le=OffsetPaginationParams.MAX_INT32)] = 0
    sorting_field: Annotated[UserSortingField, Field()] = UserSortingField.UPDATED_AT
    sorting_order: Annotated[SortingOrder, Field()] = SortingOrder.DESC


def make_list_users_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            PaginationError: status.HTTP_400_BAD_REQUEST,
            ReaderError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        description=getdoc(ListUsers),
    )
    @inject
    async def list_users(
        request_schema: Annotated[ListUsersRequestSchema, Depends()],
        interactor: FromDishka[ListUsers],
    ) -> ListUsersQm:
        request = ListUsersRequest(
            limit=request_schema.limit,
            offset=request_schema.offset,
            sorting_field=request_schema.sorting_field,
            sorting_order=request_schema.sorting_order,
        )
        return await interactor.execute(request)

    return router
