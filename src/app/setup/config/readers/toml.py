from pathlib import Path
from typing import Any

import rtoml

from app.setup.config.readers.abstract import ConfigReader


class TomlConfigReader(ConfigReader):
    def read(self, path: Path) -> dict[str, Any]:
        with open(path, mode="r", encoding="utf-8") as f:
            return rtoml.load(f)
