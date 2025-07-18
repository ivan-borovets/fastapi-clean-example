from abc import abstractmethod
from typing import Protocol


class AuthSessionTransactionManager(Protocol):
    """
    Defined to allow easier mocking and swapping
    of implementations in the same layer.

    UOW-compatible interface for flushing and
    committing changes to the data source.
    The actual implementation of UOW can be bundled with an ORM,
    like SQLAlchemy's session.
    """

    @abstractmethod
    async def commit(self) -> None:
        """
        Persist changes to the data source.

        :raises DataMapperError:
        """
