from abc import abstractmethod
from typing import Protocol


class Flusher(Protocol):
    """
    Interface for flushing intermediate changes during a business transaction.
    """

    @abstractmethod
    async def flush(self) -> None:
        """
        Flush pending changes to validate constraints or trigger side effects.

        :raises DataMapperError:
        :raises UsernameAlreadyExists:
        """
