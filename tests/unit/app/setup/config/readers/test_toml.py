from pathlib import Path

import pytest
import rtoml

from app.setup.config.readers.toml import TomlConfigReader


def test_read_valid_toml(
    toml_reader: TomlConfigReader,
    tmp_path: Path,
    test_toml_data: dict,
):
    test_config: Path = tmp_path / "test_config.toml"
    with open(test_config, "w") as f:
        rtoml.dump(test_toml_data, f)
    result: dict = toml_reader.read(test_config)
    assert result == test_toml_data


def test_read_nonexistent_file(toml_reader: TomlConfigReader):
    with pytest.raises(FileNotFoundError):
        toml_reader.read(Path("nonexistent_file.toml"))


def test_read_invalid_toml(
    toml_reader: TomlConfigReader,
    tmp_path: Path,
):
    test_config: Path = tmp_path / "invalid_config.toml"
    with open(test_config, "w") as f:
        f.write("invalid = toml [ content")
    with pytest.raises(rtoml.TomlParsingError):
        toml_reader.read(test_config)
