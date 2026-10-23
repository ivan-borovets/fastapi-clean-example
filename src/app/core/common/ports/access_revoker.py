from abc import abstractmethod
from typing import Protocol

from app.core.common.entities.types_ import UserId


class AccessRevoker(Protocol):
    @abstractmethod
    async def remove_all_user_access(self, user_id: UserId) -> None: ...
