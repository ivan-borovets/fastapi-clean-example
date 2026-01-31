from pathlib import Path
import tomllib

from app.application.common.ports.app_version_provider import AppVersionProvider


class PyprojectAppVersionProvider(AppVersionProvider):
    def __init__(self, pyproject_path: Path | None = None) -> None:
        if pyproject_path is None:
            pyproject_path = (
                Path(__file__).resolve().parents[4] / "pyproject.toml"
            )
        self._pyproject_path = pyproject_path
        self._version = self._load_version()

    def _load_version(self) -> str:
        if not self._pyproject_path.is_file():
            raise FileNotFoundError(
                f"pyproject.toml not found at {self._pyproject_path}"
            )
        raw = self._pyproject_path.read_text()
        data = tomllib.loads(raw)
        try:
            return data["project"]["version"]
        except KeyError as exc:
            raise KeyError(
                "Missing [project].version in pyproject.toml"
            ) from exc

    def get_version(self) -> str:
        return self._version
