__all__ = ("SessionRecord",)

from sqlalchemy import UUID, Column, DateTime, String, Table
from sqlalchemy.orm import composite

from app.application.user.record_session import SessionRecord
from app.domain.user.vo_user import UserId
from app.infrastructure.persistence.sqla.orm_registry import mapper_registry

sessions_table = Table(
    "sessions",
    mapper_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("expiration", DateTime(timezone=True), nullable=False),
)

mapper_registry.map_imperatively(
    SessionRecord,
    sessions_table,
    properties={
        "id_": sessions_table.c.id,
        "user_id": composite(UserId, sessions_table.c.user_id),
        "expiration": sessions_table.c.expiration,
    },
    column_prefix="_",
)
