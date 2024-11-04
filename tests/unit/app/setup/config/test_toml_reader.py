from pathlib import Path
from typing import Any

import pytest
import rtoml

from app.setup.config.toml_reader import TomlConfigReader


def test_read_valid_toml(
    toml_reader: TomlConfigReader,
    tmp_path: Path,
    test_toml_data: dict[str, dict[str, Any]],
) -> None:
    test_config: Path = tmp_path / "test_config.toml"

    with open(test_config, "w", encoding="utf-8") as f:
        rtoml.dump(test_toml_data, f)

    result: dict[str, Any] = toml_reader.read(test_config)
    assert result == test_toml_data


def test_read_nonexistent_file(toml_reader: TomlConfigReader) -> None:
    with pytest.raises(FileNotFoundError):
        toml_reader.read(Path("nonexistent_file.toml"))


def test_read_invalid_toml(
    toml_reader: TomlConfigReader,
    tmp_path: Path,
) -> None:
    test_config: Path = tmp_path / "invalid_config.toml"

    with open(test_config, "w", encoding="utf-8") as f:
        f.write("invalid = toml [ content")

    with pytest.raises(rtoml.TomlParsingError):
        toml_reader.read(test_config)
