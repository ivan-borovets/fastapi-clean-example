from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, LargeBinary, String, Table
from sqlalchemy.orm import composite

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime
from app.infrastructure.persistence_sqla.registry import mapper_registry

users_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("username", String(Username.MAX_LEN), nullable=False, unique=True),
    Column("password_hash", LargeBinary, nullable=False),
    Column(
        "role",
        Enum(
            UserRole,
            name="user_role",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    ),
    Column("is_active", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_users_table() -> None:
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "id_": users_table.c.id,
            "username": composite(Username, users_table.c.username),
            "password_hash": users_table.c.password_hash,
            "role": users_table.c.role,
            "is_active": users_table.c.is_active,
            "_created_at": composite(UtcDatetime, users_table.c.created_at),
            "updated_at": composite(UtcDatetime, users_table.c.updated_at),
        },
        column_prefix="__",
    )
