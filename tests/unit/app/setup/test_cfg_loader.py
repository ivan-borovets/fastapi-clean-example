from app.setup.config.loader import BASE_DIR_PATH


def test_base_dir_points_to_root() -> None:
    assert (BASE_DIR_PATH / "pyproject.toml").exists()
