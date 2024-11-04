from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ConfigReader(ABC):
    @abstractmethod
    def read(self, path: Path) -> dict[str, Any]: ...
