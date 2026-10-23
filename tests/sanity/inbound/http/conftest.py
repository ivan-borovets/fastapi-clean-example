from copy import deepcopy
from typing import Any

import pytest
from fastapi import FastAPI

from app.inbound.http.root_router import make_fastapi_root_router
from app.main.config.settings import CookieSettings


@pytest.fixture(scope="session")
def generated_openapi_document() -> dict[str, Any]:
    app = FastAPI()
    app.include_router(make_fastapi_root_router(debug=False, cookie_name=CookieSettings().NAME))
    return app.openapi()


@pytest.fixture
def openapi_document(generated_openapi_document: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(generated_openapi_document)
