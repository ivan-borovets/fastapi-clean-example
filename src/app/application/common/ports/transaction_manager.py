from abc import abstractmethod
from typing import Protocol


class TransactionManager(Protocol):
    """
    UoW-compatible interface for committing a business transaction.
    May be extended with rollback support.
    The implementation may be an ORM session, such as SQLAlchemy's.
    """

    @abstractmethod
    async def commit(self) -> None:
        """
        :raises DataMapperError:

        Commit the successful outcome of a business transaction.
        """
