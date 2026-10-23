from abc import abstractmethod
from typing import Protocol

from app.core.common.entities.types_ import UserId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserId: ...
