from abc import abstractmethod
from typing import Protocol


class AppVersionProvider(Protocol):
    @abstractmethod
    def get_version(self) -> str:
        """Return current app version."""
