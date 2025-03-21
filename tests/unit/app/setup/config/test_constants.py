from pathlib import Path

from app.setup.config.constants import BASE_DIR_PATH


def test_base_dir() -> None:
    expected = Path(__file__).parent.parent.parent.parent.parent.parent
    assert expected == BASE_DIR_PATH
