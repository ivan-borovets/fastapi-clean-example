import httpx2
from fastapi import status


async def test_liveness_probe(smoke_fastapi_client: httpx2.AsyncClient) -> None:
    r = await smoke_fastapi_client.get("/livez")

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == "OK"


async def test_readiness_probe(smoke_fastapi_client: httpx2.AsyncClient) -> None:
    r = await smoke_fastapi_client.get("/healthz")

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == "OK"
