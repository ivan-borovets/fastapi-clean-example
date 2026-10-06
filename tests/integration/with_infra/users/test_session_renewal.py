import httpx2
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.user import User
from app.main.config.settings import CookieSettings, SessionSettings
from app.outbound.auth_ctx.model import AuthSession
from tests.integration.with_infra.factories import create_raw_now, create_utc_datetime
from tests.integration.with_infra.users.constants import USERS_ENDPOINT


async def test_returns_200_and_extends_session_when_session_nears_expiration(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_auth_session_settings: SessionSettings,
    it_cookie_settings: CookieSettings,
    it_authenticated_admin: User,
) -> None:
    result = await it_session.execute(select(AuthSession))
    auth_session = result.scalar_one()
    refresh_window = it_auth_session_settings.ttl * it_auth_session_settings.REFRESH_THRESHOLD_RATIO
    near_expiration = create_utc_datetime(create_raw_now() + refresh_window / 2)
    auth_session.expiration = near_expiration
    await it_session.commit()

    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 200
    assert it_cookie_settings.NAME in r.cookies
    await it_session.refresh(auth_session)
    assert auth_session.expiration > near_expiration
