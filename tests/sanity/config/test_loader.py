from app.config.loader import BASE_DIR


def test_base_dir_points_to_root() -> None:
    assert (BASE_DIR / "pyproject.toml").exists()
