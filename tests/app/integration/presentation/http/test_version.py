from pathlib import Path
import tomllib

from fastapi.testclient import TestClient


def _expected_version() -> str:
    pyproject_path = Path(__file__).resolve().parents[5] / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text())
    return data["project"]["version"]


def test_version_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload == {"version": _expected_version()}
