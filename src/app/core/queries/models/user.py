from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserQm:
    id: UUID
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
