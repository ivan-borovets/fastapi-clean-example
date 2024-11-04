from pydantic import BaseModel, Field

from app.domain.entities.user.role_enum import UserRoleEnum


class CreateUserRequestPydantic(BaseModel):
    username: str
    password: str
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)
