from pathlib import Path
from typing import Any

import rtoml


class TomlConfigReader:
    def read(self, path: Path) -> dict[str, Any]:
        with open(path, mode="r", encoding="utf-8") as f:
            return rtoml.load(f)
