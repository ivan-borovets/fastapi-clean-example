from pydantic import BaseModel, Field

from app.domain.user.enums import UserRoleEnum


class CreateUserRequestPydantic(BaseModel):
    username: str
    password: str
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)
