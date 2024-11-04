from abc import abstractmethod
from typing import Protocol


class TransactionManager(Protocol):
    """
    Transaction Manager is an UOW-compatible interface for
    flushing and committing changes to the data source.
    The actual implementation of UOW can be bundled with an ORM,
    like SQLAlchemy's session.
    """

    @abstractmethod
    async def flush(self) -> None:
        """
        :raises DataMapperError:
        :raises UsernameAlreadyExists:

        Mostly to check data source constraints.
        """

    @abstractmethod
    async def commit(self) -> None:
        """
        :raises DataMapperError:

        Persist changes to the data source.
        """
