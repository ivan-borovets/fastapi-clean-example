from app.core.common.entities.base import Entity
from app.core.common.entities.types_ import UserId, UserPasswordHash, UserRole
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime


class User(Entity[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        username: Username,
        password_hash: UserPasswordHash,
        role: UserRole,
        is_active: bool,
        created_at: UtcDatetime,
        updated_at: UtcDatetime,
    ) -> None:
        super().__init__(id_=id_)
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self._created_at = created_at
        self.updated_at = updated_at

    @property
    def created_at(self) -> UtcDatetime:
        return self._created_at
