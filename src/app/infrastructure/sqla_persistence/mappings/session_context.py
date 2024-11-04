__all__ = ("SessionRecord",)

from sqlalchemy import UUID, Column, DateTime, String, Table
from sqlalchemy.orm import composite

from app.domain.entities.user.value_objects import UserId
from app.infrastructure.session_context.common.session_record import SessionRecord
from app.infrastructure.sqla_persistence.orm_registry import mapping_registry

sessions_table = Table(
    "sessions",
    mapping_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("expiration", DateTime(timezone=True), nullable=False),
)

mapping_registry.map_imperatively(
    SessionRecord,
    sessions_table,
    properties={
        "id_": sessions_table.c.id,
        "user_id": composite(UserId, sessions_table.c.user_id),
        "expiration": sessions_table.c.expiration,
    },
    column_prefix="_",
)
