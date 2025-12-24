import pytest
from pydantic import PostgresDsn, ValidationError

from app.setup.config.database import PORT_MAX, PORT_MIN, PostgresSettings
from tests.app.unit.factories.settings_data import create_postgres_settings_data


def test_postgres_host_overridden_by_env_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_host = "changed"
    monkeypatch.setenv("POSTGRES_HOST", env_host)
    data = create_postgres_settings_data(host="initial")

    sut = PostgresSettings.model_validate(data)

    assert sut.host == env_host


@pytest.mark.parametrize(
    "port",
    [
        pytest.param(PORT_MIN, id="lower_bound"),
        pytest.param(PORT_MAX, id="upper_bound"),
    ],
)
def test_postgres_port_accepts_correct_value(port: int) -> None:
    data = create_postgres_settings_data(port=port)

    PostgresSettings.model_validate(data)


@pytest.mark.parametrize(
    "port",
    [
        pytest.param(PORT_MIN - 1, id="too_small"),
        pytest.param(PORT_MAX + 1, id="too_big"),
    ],
)
def test_postgres_port_rejects_incorrect_value(port: int) -> None:
    data = create_postgres_settings_data(port=port)

    with pytest.raises(ValidationError):
        PostgresSettings.model_validate(data)


def test_postgres_dsn_builds_valid_uri_from_fields() -> None:
    data = create_postgres_settings_data(
        user="alice",
        password="secret",
        db="my_db",
        host="localhost",
        port=5678,
        driver="psycopg2",
    )

    sut = PostgresSettings.model_validate(data)

    assert sut.dsn == "postgresql+psycopg2://alice:secret@localhost:5678/my_db"
    assert PostgresDsn(sut.dsn)
