from collections.abc import AsyncIterator

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from app.main.run import make_app


@pytest.fixture
def smoke_app() -> FastAPI:
    return make_app()


@pytest.fixture
async def smoke_client(smoke_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with (
        LifespanManager(smoke_app, startup_timeout=60) as manager,
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=manager.app),
            base_url="http://test",
        ) as client,
    ):
        yield client
