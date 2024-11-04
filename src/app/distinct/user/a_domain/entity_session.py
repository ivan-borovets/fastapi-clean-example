from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from app.base.a_domain.entity import Entity
from app.distinct.user.a_domain.vo_session import SessionExpiration, SessionId
from app.distinct.user.a_domain.vo_user import UserId


@dataclass(eq=False, slots=True, kw_only=True)
class Session(Entity[SessionId]):
    user_id: UserId
    expiration: SessionExpiration

    @classmethod
    def create(cls, *, session_id: str, user_id: UUID, expiration: datetime) -> Self:
        return cls(
            id_=SessionId(session_id),
            user_id=UserId(user_id),
            expiration=SessionExpiration(expiration),
        )

    def extend(self, new_expiration: datetime) -> None:
        self.expiration = SessionExpiration(new_expiration)
