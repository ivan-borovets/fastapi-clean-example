from dataclasses import dataclass

from app.domain.entities.base.entity import Entity
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import UserId, Username, UserPasswordHash


@dataclass(eq=False, kw_only=True)
class User(Entity[UserId]):
    username: Username
    password_hash: UserPasswordHash
    role: UserRoleEnum
    is_active: bool
