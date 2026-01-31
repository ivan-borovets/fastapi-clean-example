import pytest
from fastapi.testclient import TestClient

from app.run import make_app
from app.setup.config.loader import ValidEnvs
from app.setup.config.settings import load_settings


@pytest.fixture(scope="module")
def client() -> TestClient:
    settings = load_settings(env=ValidEnvs.LOCAL)
    app = make_app(settings=settings)
    with TestClient(app) as test_client:
        yield test_client
