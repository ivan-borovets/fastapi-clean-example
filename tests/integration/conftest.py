import os
from collections.abc import Iterator
from typing import Final

import pytest
from sqlalchemy import Engine, NullPool, create_engine, make_url, text

from app.main.config.loader import load_postgres_settings
from app.main.config.settings import PostgresSettings

ALLOW_DESTRUCTIVE_TEST_CLEANUP: Final[str] = "ALLOW_DESTRUCTIVE_TEST_CLEANUP"
ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE: Final[str] = "1"
TEMPLATE_DB_EXTENSIONS: Final[tuple[str, ...]] = ()


@pytest.fixture(scope="session")
def allow_destructive() -> None:
    """Use on fixtures that require potentially dangerous cleanup."""
    if os.getenv(ALLOW_DESTRUCTIVE_TEST_CLEANUP) != ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE:
        raise pytest.UsageError(
            "Destructive cleanup is disabled: "
            f"{ALLOW_DESTRUCTIVE_TEST_CLEANUP} must be set to {ALLOW_DESTRUCTIVE_TEST_CLEANUP_EXPECTED_VALUE}. "
            "This guard prevents accidental cleanup of non-test data."
        )


@pytest.fixture(scope="session")
def it_postgres_settings() -> PostgresSettings:
    return load_postgres_settings()


@pytest.fixture(scope="session")
def it_maintenance_db_engine(it_postgres_settings: PostgresSettings) -> Iterator[Engine]:
    """`CREATE DATABASE` cannot run in a transaction, hence AUTOCOMMIT; `NullPool` keeps an idle worker unconnected."""
    url = make_url(it_postgres_settings.dsn).set(database="postgres")
    engine = create_engine(url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def it_template_postgres_settings(
    allow_destructive: None,
    it_postgres_settings: PostgresSettings,
    it_maintenance_db_engine: Engine,
    worker_id: str,
) -> PostgresSettings:
    """One per worker: `CREATE DATABASE ... TEMPLATE` fails while the template has other sessions."""
    settings = PostgresSettings(
        DB=f"{it_postgres_settings.DB}_{worker_id}_template",
        HOST=it_postgres_settings.HOST,
        PORT=it_postgres_settings.PORT,
        USER=it_postgres_settings.USER,
        PASSWORD=it_postgres_settings.PASSWORD,
    )

    with it_maintenance_db_engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{settings.DB}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{settings.DB}"'))

    extensions_engine = create_engine(settings.dsn, poolclass=NullPool)
    with extensions_engine.begin() as connection:
        for extension in TEMPLATE_DB_EXTENSIONS:
            connection.execute(text(f"CREATE EXTENSION {extension}"))
    extensions_engine.dispose()

    return settings
