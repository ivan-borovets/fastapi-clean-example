from abc import abstractmethod
from typing import Protocol


class UserTransactionManager(Protocol):
    """
    Defined to allow easier mocking and swapping
    of implementations in the same layer.

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
