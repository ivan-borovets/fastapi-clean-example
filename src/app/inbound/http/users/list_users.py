from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field
from starlette import status

from app.core.common.authorization.exceptions import AuthorizationError
from app.core.queries.list_users import ListUsers, ListUsersRequest, UserSortingField
from app.core.queries.ports.user_reader import ListUsersQm
from app.core.queries.query_support.exceptions import PaginationError
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingOrder
from app.inbound.http.errors.callbacks import log_info
from app.inbound.http.errors.router import make_error_aware_router
from app.inbound.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.exceptions import ReaderError, StorageError


class ListUsersRequestSchema(BaseModel):
    """
    Using Pydantic model here is generally unnecessary.
    It's only implemented to render specific Swagger UI.
    """

    model_config = ConfigDict(frozen=True)

    limit: int = Field(default=20, ge=OffsetPaginationParams.MIN_LIMIT, le=OffsetPaginationParams.MAX_INT32)
    offset: int = Field(default=0, ge=OffsetPaginationParams.MIN_OFFSET, le=OffsetPaginationParams.MAX_INT32)
    sorting_field: UserSortingField = UserSortingField.UPDATED_AT
    sorting_order: SortingOrder = SortingOrder.DESC

    def to_request(self) -> ListUsersRequest:
        return ListUsersRequest(
            limit=self.limit,
            offset=self.offset,
            sorting_field=self.sorting_field,
            sorting_order=self.sorting_order,
        )


def make_list_users_router() -> APIRouter:
    router = make_error_aware_router(on_error=log_info)

    @router.get(
        "/",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            StorageError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            PaginationError: status.HTTP_400_BAD_REQUEST,
            ReaderError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
        },
        status_code=status.HTTP_200_OK,
        description=getdoc(ListUsers),
    )
    @inject
    async def list_users(
        request_schema: Annotated[ListUsersRequestSchema, Query()],
        interactor: FromDishka[ListUsers],
    ) -> ListUsersQm:
        return await interactor.execute(request_schema.to_request())

    return router
