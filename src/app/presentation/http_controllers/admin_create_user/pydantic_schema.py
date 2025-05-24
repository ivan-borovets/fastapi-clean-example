from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.user_role import UserRole


class CreateUserRequestPydantic(BaseModel):
    """
    Using a Pydantic model here is generally unnecessary.
    It's only implemented to render a specific Swagger UI (OpenAPI) schema.
    """

    model_config = ConfigDict(frozen=True)

    username: str
    password: str
    role: UserRole = Field(default=UserRole.USER)
