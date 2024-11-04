from datetime import timedelta
from pathlib import Path

import pytest
from pydantic import PostgresDsn, ValidationError

from app.setup.config.toml_reader import TomlConfigReader
from app.setup.config.settings import LoggingSettings, SessionSettings, Settings


def test_settings_from_file(mock_config_reader: TomlConfigReader, tmp_path: Path):
    fake_path: Path = tmp_path / "test_config.toml"
    fake_path.touch()
    settings: Settings = Settings.from_file(
        path=fake_path,
        reader=mock_config_reader,
    )

    assert settings.security.password.pepper == "test_pepper"
    assert settings.security.session.jwt_secret == "test_secret"
    assert settings.security.session.jwt_algorithm == "HS256"
    assert settings.security.session.session_ttl_min == timedelta(minutes=123)
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


def test_settings_from_file_not_found(mock_config_reader: TomlConfigReader):
    fake_path: Path = Path("fake_path")

    with pytest.raises(FileNotFoundError):
        Settings.from_file(fake_path, mock_config_reader)


def test_jwt_algorithm_validation():
    for algo in (
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
    ):
        SessionSettings(
            JWT_SECRET="test_secret",
            JWT_ALGORITHM=algo,  # type: ignore
            SESSION_TTL_MIN=123,  # type: ignore
            SESSION_REFRESH_THRESHOLD=0.5,
        )

    with pytest.raises(ValidationError):
        SessionSettings(
            JWT_SECRET="test_secret",
            JWT_ALGORITHM="TEST1",  # type: ignore
            SESSION_TTL_MIN=123,  # type: ignore
            SESSION_REFRESH_THRESHOLD=0.5,
        )


def test_logging_settings_validation():
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        LoggingSettings(LOG_LEVEL=level)  # type: ignore

    with pytest.raises(ValidationError):
        LoggingSettings(LOG_LEVEL="INVALID_LEVEL")  # type: ignore


def test_session_ttl_min_invalid_value():
    with pytest.raises(ValueError, match="SESSION_TTL_MIN must be at least 1"):
        SessionSettings(
            SESSION_TTL_MIN=0.5,  # type: ignore
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD=1,
        )


def test_session_ttl_min_invalid_type():
    with pytest.raises(ValueError, match="SESSION_TTL_MIN must be a number"):
        SessionSettings(
            SESSION_TTL_MIN="one",  # type: ignore
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD=1,
        )


def test_session_refresh_threshold_invalid_value():
    with pytest.raises(
        ValueError, match="SESSION_REFRESH_THRESHOLD must be between 0 and 1, exclusive"
    ):
        SessionSettings(
            SESSION_TTL_MIN=2,  # type: ignore
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD=1.5,
        )


def test_session_refresh_threshold_invalid_type():
    with pytest.raises(ValueError, match="SESSION_REFRESH_THRESHOLD must be a number"):
        SessionSettings(
            SESSION_TTL_MIN=2,  # type: ignore
            JWT_SECRET="secret",
            JWT_ALGORITHM="HS256",
            SESSION_REFRESH_THRESHOLD="high",  # type: ignore
        )
