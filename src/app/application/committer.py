from abc import abstractmethod
from typing import Protocol


class Committer(Protocol):
    """
    Committer is an UOW-compatible interface for committing changes to the data source.
    The actual implementation of UOW can be bundled with an ORM,
    like SQLAlchemy's session.
    """

    @abstractmethod
    async def commit(self) -> None:
        """
        :raises DataGatewayError:
        """
