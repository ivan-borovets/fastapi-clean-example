from abc import abstractmethod
from typing import Protocol


class TransactionManager(Protocol):
    """
    UOW-compatible interface for flushing and
    committing changes to the data source.
    The actual implementation of UOW can be bundled with an ORM,
    like SQLAlchemy's session.
    """

    @abstractmethod
    async def flush(self) -> None:
        """
        Mostly to check data source constraints.

        :raises DataMapperError:
        :raises UsernameAlreadyExists:
        """

    @abstractmethod
    async def commit(self) -> None:
        """
        Persist changes to the data source.

        :raises DataMapperError:
        """
