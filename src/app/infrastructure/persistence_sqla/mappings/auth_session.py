from sqlalchemy import UUID, Column, DateTime, String, Table
from sqlalchemy.orm import composite

from app.domain.value_objects.user_id import UserId
from app.infrastructure.auth.session.model import AuthSession
from app.infrastructure.persistence_sqla.registry import mapper_registry

auth_sessions_table = Table(
    "auth_sessions",
    mapper_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("expiration", DateTime(timezone=True), nullable=False),
)


def map_auth_sessions_table() -> None:
    mapper_registry.map_imperatively(
        AuthSession,
        auth_sessions_table,
        properties={
            "id_": auth_sessions_table.c.id,
            "user_id": composite(UserId, auth_sessions_table.c.user_id),
            "expiration": auth_sessions_table.c.expiration,
        },
        column_prefix="_",
    )
