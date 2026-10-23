from abc import abstractmethod
from typing import Protocol


class Flusher(Protocol):
    """Interface for flushing intermediate changes during a business transaction."""

    @abstractmethod
    async def flush(self) -> None:
        """Flush pending changes when their effect is needed before commit, e.g. constraint checks, DB-generated IDs."""
