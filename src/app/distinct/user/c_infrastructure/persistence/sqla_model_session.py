__all__ = ("Session",)

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import composite

from app.common.c_infrastructure.persistence.sqla.orm_registry import mapper_registry
from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.vo_session import SessionExpiration, SessionId
from app.distinct.user.a_domain.vo_user import UserId

sessions_table = Table(
    "sessions",
    mapper_registry.metadata,
    Column("id", String, primary_key=True),
    Column("user_id", ForeignKey("users.id")),
    Column("expiration", DateTime(timezone=True), nullable=False),
)

mapper_registry.map_imperatively(
    Session,
    sessions_table,
    properties={
        "id_": composite(SessionId, sessions_table.c.id),
        "user_id": composite(UserId, sessions_table.c.user_id),
        "expiration": composite(SessionExpiration, sessions_table.c.expiration),
    },
    column_prefix="_",
)
