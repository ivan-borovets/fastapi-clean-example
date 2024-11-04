from sqlalchemy import UUID, Boolean, Column, Enum, LargeBinary, String, Table
from sqlalchemy.orm import composite

from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.validation.constants import USERNAME_MAX_LEN
from app.domain.entities.user.value_objects import UserId, Username, UserPasswordHash
from app.infrastructure.sqla_persistence.orm_registry import mapping_registry

users_table = Table(
    "users",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("username", String(USERNAME_MAX_LEN), nullable=False, unique=True),
    Column("password_hash", LargeBinary, nullable=False),
    Column(
        "role",
        Enum(UserRoleEnum),
        default=UserRoleEnum.USER,
        nullable=False,
    ),
    Column("is_active", Boolean, default=True, nullable=False),
)


def map_users_table() -> None:
    mapping_registry.map_imperatively(
        User,
        users_table,
        properties={
            "id_": composite(UserId, users_table.c.id),
            "username": composite(Username, users_table.c.username),
            "password_hash": composite(UserPasswordHash, users_table.c.password_hash),
            "role": users_table.c.role,
            "is_active": users_table.c.is_active,
        },
        column_prefix="_",
    )
