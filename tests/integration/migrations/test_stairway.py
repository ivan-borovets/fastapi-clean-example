"""
Test can find forgotten downgrade methods, undeleted data types in downgrade
methods, typos and many other errors.

Does not require any maintenance - you just add it once to check 80% of typos
and mistakes in migrations forever.

https://github.com/alvassin/alembic-quickstart
"""

from typing import Final

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.script import Script, ScriptDirectory

from app.main.config.loader import BASE_DIR
from app.main.config.settings import PostgresSettings

ALEMBIC_INI_PATH: Final[str] = str(BASE_DIR / "alembic.ini")


@pytest.fixture
def alembic_config(migration_stairway_settings: PostgresSettings) -> Config:
    return Config(ALEMBIC_INI_PATH, attributes={"postgres_settings": migration_stairway_settings})


def get_revisions() -> list[Script]:
    # Create Alembic configuration object
    # (we don't need database for getting revisions list)
    config = Config(ALEMBIC_INI_PATH)

    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    return revisions


@pytest.mark.parametrize("revision", get_revisions())
def test_migrations_stairway(
    alembic_config: Config,
    revision: Script,
) -> None:
    upgrade(alembic_config, revision.revision)

    # We need -1 for downgrading first migration (its down_revision is None)
    downgrade(alembic_config, str(revision.down_revision or "-1"))
    upgrade(alembic_config, revision.revision)
