from datetime import timedelta
from pathlib import Path

import pytest
from pydantic import PostgresDsn, ValidationError

from app.setup.config.settings import AuthSettings, LoggingSettings, Settings
from app.setup.config.toml_reader import TomlConfigReader


def test_settings_from_file(
    mock_config_reader: TomlConfigReader,
    tmp_path: Path,
) -> None:
    config_path: Path = tmp_path / "test_config.toml"
    config_path.touch()
    settings: Settings = Settings.from_file(
        path=config_path,
        reader=mock_config_reader,
    )

    assert settings.security.password.pepper == "test_pepper"
    assert settings.security.auth.jwt_secret == "test_secret"
    assert settings.security.auth.jwt_algorithm == "HS256"
    assert settings.security.auth.session_ttl_min == timedelta(minutes=123)
    assert settings.security.password.pepper == "test_pepper"
    assert settings.security.cookies.secure is False

    assert settings.logging.level == "WARNING"

    assert settings.db.postgres.username == "test_user"
    assert settings.db.postgres.password == "test_password"
    assert settings.db.postgres.host == "test_host"
    assert settings.db.postgres.port == 1234
    assert settings.db.postgres.path == "test_db"

    assert settings.db.postgres.dsn == str(
        PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=settings.db.postgres.username,
            password=settings.db.postgres.password,
            host=settings.db.postgres.host,
            port=settings.db.postgres.port,
            path=settings.db.postgres.path,
        )
    )

    assert settings.db.sqla_engine.echo is True
    assert settings.db.sqla_engine.echo_pool is False
    assert settings.db.sqla_engine.pool_size == 1
    assert settings.db.sqla_engine.max_overflow == 0


def test_settings_from_file_not_found(mock_config_reader: TomlConfigReader) -> None:
    with pytest.raises(FileNotFoundError):
        Settings.from_file(Path("fake_path"), mock_config_reader)


def test_jwt_algorithm_validation():
    valid_algos: list[str] = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
    base_settings: dict[str, str | int | float] = {
        "JWT_SECRET": "test_secret",
        "SESSION_TTL_MIN": 123,
        "SESSION_REFRESH_THRESHOLD": 0.5,
    }

    for algo in valid_algos:
        AuthSettings(**base_settings, JWT_ALGORITHM=algo)

    with pytest.raises(ValidationError):
        AuthSettings(**base_settings, JWT_ALGORITHM="INVALID")


def test_logging_settings_validation() -> None:
    valid_levels: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in valid_levels:
        LoggingSettings(LOG_LEVEL=level)

    with pytest.raises(ValidationError):
        LoggingSettings(LOG_LEVEL="INVALID_LEVEL")


def test_auth_session_ttl_min_invalid_value() -> None:
    with pytest.raises(ValueError, match="SESSION_TTL_MIN must be at least 1"):
        AuthSettings(
            SESSION_TTL_MIN=0.5,
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD=1,
        )


def test_auth_session_ttl_min_invalid_type() -> None:
    with pytest.raises(ValueError, match="SESSION_TTL_MIN must be a number"):
        AuthSettings(
            SESSION_TTL_MIN="one",
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD=1,
        )


def test_auth_session_refresh_threshold_invalid_value() -> None:
    with pytest.raises(
        ValueError, match="SESSION_REFRESH_THRESHOLD must be between 0 and 1, exclusive"
    ):
        AuthSettings(
            SESSION_TTL_MIN=2,
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD=1.5,
        )


def test_auth_session_refresh_threshold_invalid_type() -> None:
    with pytest.raises(ValueError, match="SESSION_REFRESH_THRESHOLD must be a number"):
        AuthSettings(
            SESSION_TTL_MIN=2,
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD="high",
        )
