import httpx


async def authenticate(client: httpx.AsyncClient, username: str, password: str) -> None:
    r = await client.post("/api/v1/account/login/", json={"username": username, "password": password})
    assert r.status_code == 204
