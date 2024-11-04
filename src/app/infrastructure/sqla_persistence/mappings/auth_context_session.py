from sqlalchemy import UUID, Column, DateTime, String, Table
from sqlalchemy.orm import composite

from app.domain.entities.user.value_objects import UserId
from app.infrastructure.auth_context.common.auth_session import AuthSession
from app.infrastructure.sqla_persistence.orm_registry import mapping_registry

auth_sessions_table = Table(
    "auth_sessions",
    mapping_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("expiration", DateTime(timezone=True), nullable=False),
)


def map_auth_sessions_table() -> None:
    mapping_registry.map_imperatively(
        AuthSession,
        auth_sessions_table,
        properties={
            "id_": auth_sessions_table.c.id,
            "user_id": composite(UserId, auth_sessions_table.c.user_id),
            "expiration": auth_sessions_table.c.expiration,
        },
        column_prefix="_",
    )
