import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.services.user import UserService
from tests.integration.with_infra.account.constants import AUTH_COOKIE_NAME, LOG_OUT_ENDPOINT
from tests.integration.with_infra.authentication import authenticate
from tests.integration.with_infra.factories import create_raw_password, create_user_with_password


async def test_returns_204_and_clears_cookie(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    it_session.add(user)
    await it_session.commit()
    await authenticate(it_client, user.username.value, password)

    r = await it_client.delete(LOG_OUT_ENDPOINT)

    assert r.status_code == 204
    assert AUTH_COOKIE_NAME not in it_client.cookies


async def test_returns_401_when_not_authenticated(
    it_client: httpx.AsyncClient,
) -> None:
    r = await it_client.delete(LOG_OUT_ENDPOINT)

    assert r.status_code == 401
