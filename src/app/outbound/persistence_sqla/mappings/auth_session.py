from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import composite

from app.core.common.value_objects.utc_datetime import UtcDatetime
from app.outbound.auth_ctx.model import AuthSession
from app.outbound.persistence_sqla.registry import mapper_registry

auth_sessions_table = Table(
    "auth_sessions",
    mapper_registry.metadata,
    Column("id", String, primary_key=True),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("expiration", DateTime(timezone=True), nullable=False),
)


def map_auth_sessions_table() -> None:
    mapper_registry.map_imperatively(
        AuthSession,
        auth_sessions_table,
        properties={
            "id_": auth_sessions_table.c.id,
            "user_id": auth_sessions_table.c.user_id,
            "expiration": composite(UtcDatetime, auth_sessions_table.c.expiration),
        },
        column_prefix="__",
    )
