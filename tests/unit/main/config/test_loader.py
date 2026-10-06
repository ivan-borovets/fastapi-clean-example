import pytest

from app.main.config.loader import (
    load_app_settings,
    load_cookie_settings,
    load_jwt_settings,
    load_password_hasher_settings,
    load_postgres_settings,
    load_session_settings,
    load_sqla_settings,
)


@pytest.mark.parametrize("logging_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_load_app_settings_reads_env_vars(monkeypatch: pytest.MonkeyPatch, logging_level: str) -> None:
    monkeypatch.setenv("APP_SERVICE_NAME", "test-service")
    monkeypatch.setenv("APP_VERSION", "test-version")
    monkeypatch.setenv("APP_ROOT_PATH", "test-path")
    monkeypatch.setenv("APP_DEBUG_MODE", "1")
    monkeypatch.setenv("APP_LOGGING_LEVEL", logging_level)

    sut = load_app_settings()

    assert sut.SERVICE_NAME == "test-service"
    assert sut.VERSION == "test-version"
    assert sut.ROOT_PATH == "test-path"
    assert sut.DEBUG_MODE is True
    assert sut.LOGGING_LEVEL == logging_level  # noqa: SIM300


def test_load_postgres_settings_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_HOST", "test_host")
    monkeypatch.setenv("POSTGRES_PORT", "54321")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")

    sut = load_postgres_settings()

    assert sut.DB == "test_db"
    assert sut.HOST == "test_host"
    assert sut.PORT == 54321
    assert sut.USER == "test_user"
    assert sut.PASSWORD == "test_password"  # noqa: S105


def test_load_sqla_settings_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SQLA_ECHO", "true")
    monkeypatch.setenv("SQLA_ECHO_POOL", "true")
    monkeypatch.setenv("SQLA_POOL_SIZE", "123")
    monkeypatch.setenv("SQLA_MAX_OVERFLOW", "456")
    monkeypatch.setenv("SQLA_CONNECT_TIMEOUT_S", "7")

    sut = load_sqla_settings()

    assert sut.ECHO is True
    assert sut.ECHO_POOL is True
    assert sut.POOL_SIZE == 123
    assert sut.MAX_OVERFLOW == 456
    assert sut.CONNECT_TIMEOUT_S == 7


def test_load_password_hasher_settings_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PASSWORD_PEPPER", "test-pepper-test-pepper-test-pepper")
    monkeypatch.setenv("PASSWORD_WORK_FACTOR", "123456789")
    monkeypatch.setenv("PASSWORD_MAX_THREADS", "987654321")
    monkeypatch.setenv("PASSWORD_SEMAPHORE_WAIT_TIMEOUT_S", "1.23456789")

    sut = load_password_hasher_settings()

    assert sut.PEPPER == "test-pepper-test-pepper-test-pepper"
    assert sut.WORK_FACTOR == 123456789
    assert sut.MAX_THREADS == 987654321
    assert sut.SEMAPHORE_WAIT_TIMEOUT_S == 1.23456789


def test_load_jwt_settings_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-test-secret-test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS384")

    sut = load_jwt_settings()

    assert sut.SECRET == "test-secret-test-secret-test-secret"  # noqa: S105
    assert sut.ALGORITHM == "HS384"


def test_load_session_settings_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SESSION_TTL_MIN", "123465789")
    monkeypatch.setenv("SESSION_REFRESH_THRESHOLD_RATIO", "0.123456789")

    sut = load_session_settings()

    assert sut.TTL_MIN == 123465789
    assert sut.REFRESH_THRESHOLD_RATIO == 0.123456789


def test_load_cookie_settings_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COOKIE_NAME", "test-name")
    monkeypatch.setenv("COOKIE_PATH", "test-path")
    monkeypatch.setenv("COOKIE_HTTPONLY", "1")
    monkeypatch.setenv("COOKIE_SECURE", "false")
    monkeypatch.setenv("COOKIE_SAMESITE", "strict")

    sut = load_cookie_settings()

    assert sut.NAME == "test-name"
    assert sut.PATH == "test-path"
    assert sut.HTTPONLY is True
    assert sut.SECURE is False
    assert sut.SAMESITE == "strict"
