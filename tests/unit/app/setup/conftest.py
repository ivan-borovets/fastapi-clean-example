import pytest

from app.setup.config.settings import Settings
from tests.unit.app.setup.config.conftest import MockConfigReader


@pytest.fixture
def mock_settings(mock_config_reader: MockConfigReader) -> Settings:
    return Settings.from_file(reader=mock_config_reader)
