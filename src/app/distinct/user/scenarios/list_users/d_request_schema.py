from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ListUsersRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    limit: Annotated[int, Field(ge=1)] = 20
    offset: Annotated[int, Field(ge=0)] = 0
