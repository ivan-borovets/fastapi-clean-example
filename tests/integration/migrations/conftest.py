from collections.abc import Iterator
from typing import Final

import pytest
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text

from app.main.config.loader import BASE_DIR
from app.main.config.settings import PostgresSettings

ALEMBIC_INI_PATH: Final[str] = str(BASE_DIR / "alembic.ini")


@pytest.fixture(scope="session")
def migration_stairway_settings(
    allow_destructive: None,
    it_postgres_settings: PostgresSettings,
    it_maintenance_db_engine: Engine,
    it_template_postgres_settings: PostgresSettings,
) -> PostgresSettings:
    settings = PostgresSettings(
        DB=f"{it_postgres_settings.DB}_stairway",
        HOST=it_postgres_settings.HOST,
        PORT=it_postgres_settings.PORT,
        USER=it_postgres_settings.USER,
        PASSWORD=it_postgres_settings.PASSWORD,
    )

    with it_maintenance_db_engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{settings.DB}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{settings.DB}" TEMPLATE "{it_template_postgres_settings.DB}"'))

    return settings


@pytest.fixture
def migration_isolated_settings(
    allow_destructive: None,
    it_postgres_settings: PostgresSettings,
    it_maintenance_db_engine: Engine,
    it_template_postgres_settings: PostgresSettings,
) -> PostgresSettings:
    settings = PostgresSettings(
        DB=f"{it_postgres_settings.DB}_migration",
        HOST=it_postgres_settings.HOST,
        PORT=it_postgres_settings.PORT,
        USER=it_postgres_settings.USER,
        PASSWORD=it_postgres_settings.PASSWORD,
    )

    with it_maintenance_db_engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{settings.DB}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{settings.DB}" TEMPLATE "{it_template_postgres_settings.DB}"'))

    return settings


@pytest.fixture
def migration_alembic_config(migration_isolated_settings: PostgresSettings) -> Config:
    return Config(ALEMBIC_INI_PATH, attributes={"postgres_settings": migration_isolated_settings})


@pytest.fixture
def migration_engine(migration_isolated_settings: PostgresSettings) -> Iterator[Engine]:
    engine = create_engine(migration_isolated_settings.dsn)
    try:
        yield engine
    finally:
        engine.dispose()
