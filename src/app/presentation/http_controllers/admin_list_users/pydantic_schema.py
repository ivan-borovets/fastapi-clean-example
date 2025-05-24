from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.application.common.query_filters.sorting_order_enum import SortingOrder


class ListUsersRequestPydantic(BaseModel):
    """
    Using a Pydantic model here is generally unnecessary.
    It's only implemented to render a specific Swagger UI (OpenAPI) schema.
    """

    model_config = ConfigDict(frozen=True)

    limit: Annotated[int, Field(ge=1)] = 20
    offset: Annotated[int, Field(ge=0)] = 0
    sorting_field: Annotated[str | None, Field()] = None
    sorting_order: Annotated[SortingOrder | None, Field()] = None
