import httpx

from tests.integration.with_infra.account.constants import LOG_IN_ENDPOINT


async def authenticate(client: httpx.AsyncClient, username: str, password: str) -> None:
    r = await client.post(LOG_IN_ENDPOINT, json={"username": username, "password": password})
    assert r.status_code == 204
