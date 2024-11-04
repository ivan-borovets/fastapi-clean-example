from abc import abstractmethod
from typing import Protocol


class Committer(Protocol):
    @abstractmethod
    async def commit(self) -> None:
        """
        :raises GatewayError:
        """
