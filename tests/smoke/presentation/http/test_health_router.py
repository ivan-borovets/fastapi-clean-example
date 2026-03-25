import httpx
import pytest
from fastapi import FastAPI, status


async def test_liveness_probe(smoke_client: httpx.AsyncClient) -> None:
    r = await smoke_client.get("/livez/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == "OK"


async def test_readiness_probe(smoke_client: httpx.AsyncClient) -> None:
    r = await smoke_client.get("/healthz/")

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == "OK"


async def test_error_handling_prod_contract(
    smoke_client: httpx.AsyncClient,
    smoke_app: FastAPI,
) -> None:
    if smoke_app.debug:
        pytest.skip("Not applicable when DEBUG=true")

    r = await smoke_client.get("/nonexistent/")

    assert r.status_code == status.HTTP_404_NOT_FOUND
