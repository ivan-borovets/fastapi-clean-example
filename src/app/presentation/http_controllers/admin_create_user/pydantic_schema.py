from pydantic import BaseModel, Field

from app.domain.entities.user.role_enum import UserRoleEnum


class CreateUserRequestPydantic(BaseModel):
    """
    Using a Pydantic model here is generally unnecessary.
    It's only implemented to render a specific Swagger UI (OpenAPI) schema.
    """

    username: str
    password: str
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)
