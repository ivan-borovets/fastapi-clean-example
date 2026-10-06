import httpx2
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.main.config.settings import CookieSettings
from app.outbound.auth_ctx.model import AuthSession
from tests.integration.with_infra.account.constants import LOG_OUT_ENDPOINT
from tests.integration.with_infra.factories import create_utc_datetime


async def test_returns_204_and_ends_session(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_cookie_settings: CookieSettings,
    it_authenticated_user: User,
) -> None:
    r = await it_client.delete(LOG_OUT_ENDPOINT)

    assert r.status_code == 204
    assert it_cookie_settings.NAME not in it_client.cookies
    count = await it_session.scalar(select(func.count()).select_from(AuthSession))
    assert count == 0


async def test_returns_401_when_not_authenticated(
    it_client: httpx2.AsyncClient,
) -> None:
    r = await it_client.delete(LOG_OUT_ENDPOINT)

    assert r.status_code == 401


async def test_returns_401_when_session_is_terminated(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_user: User,
) -> None:
    await it_session.execute(delete(AuthSession))
    await it_session.commit()

    r = await it_client.delete(LOG_OUT_ENDPOINT)

    assert r.status_code == 401


async def test_returns_401_when_session_is_expired(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_user: User,
) -> None:
    result = await it_session.execute(select(AuthSession))
    auth_session = result.scalar_one()
    auth_session.expiration = create_utc_datetime()
    await it_session.commit()

    r = await it_client.delete(LOG_OUT_ENDPOINT)

    assert r.status_code == 401


async def test_returns_403_and_revokes_sessions_when_user_is_inactive(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
    it_authenticated_user: User,
) -> None:
    it_user_service.set_activation(it_authenticated_user, now=create_utc_datetime(), is_active=False)
    await it_session.commit()

    r = await it_client.delete(LOG_OUT_ENDPOINT)

    assert r.status_code == 403
    count = await it_session.scalar(select(func.count()).select_from(AuthSession))
    assert count == 0
