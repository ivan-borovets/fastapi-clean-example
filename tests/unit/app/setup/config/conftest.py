from pathlib import Path
from typing import Any

import pytest

from app.setup.config.readers.abstract import ConfigReader


class MockConfigReader(ConfigReader):
    def read(self, path: Path) -> dict[str, Any]:
        return {
            "security": {
                "password": {
                    "PASSWORD_PEPPER": "test_pepper",
                },
                "session": {
                    "JWT_SECRET": "test_secret",
                    "JWT_ALGORITHM": "HS256",
                    "SESSION_TTL_MIN": 123,
                    "SESSION_REFRESH_THRESHOLD": 0.5,
                },
                "cookies": {
                    "SECURE": 0,
                },
            },
            "logging": {
                "LOG_LEVEL": "WARNING",
            },
            "uvicorn": {
                "UVICORN_HOST": "test_host",
                "UVICORN_PORT": 1234,
                "UVICORN_RELOAD": True,
            },
            "db": {
                "postgres": {
                    "POSTGRES_USER": "test_user",
                    "POSTGRES_PASSWORD": "test_password",
                    "POSTGRES_HOST": "test_host",
                    "POSTGRES_PORT": 1234,
                    "POSTGRES_DB": "test_db",
                },
                "sqla_engine": {
                    "SQLA_ECHO": True,
                    "SQLA_ECHO_POOL": False,
                    "SQLA_POOL_SIZE": 1,
                    "SQLA_MAX_OVERFLOW": 0,
                },
            },
        }


@pytest.fixture
def mock_config_reader() -> MockConfigReader:
    return MockConfigReader()
