import pytest

from app.setup.config.readers.toml import TomlConfigReader


@pytest.fixture
def toml_reader() -> TomlConfigReader:
    return TomlConfigReader()


@pytest.fixture
def test_toml_data() -> dict:
    return {
        "db": {
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
            "POSTGRES_HOST": "test_host",
            "POSTGRES_PORT": 1234,
            "POSTGRES_DB": "test_db",
        }
    }
