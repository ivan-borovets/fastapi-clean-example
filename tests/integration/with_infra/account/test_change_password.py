import httpx2
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from tests.integration.with_infra.account.constants import CHANGE_PASSWORD_ENDPOINT
from tests.integration.with_infra.factories import create_password, create_raw_password


async def test_returns_204_and_changes_password(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
    it_authenticated_user: User,
    it_authenticated_user_password: str,
) -> None:
    new_password = create_raw_password()
    payload = {"current_password": it_authenticated_user_password, "new_password": new_password}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 204
    await it_session.refresh(it_authenticated_user)
    is_password_valid = await it_user_service.is_password_valid(it_authenticated_user, create_password(new_password))
    assert is_password_valid is True


async def test_returns_400_when_new_password_is_too_short(
    it_client: httpx2.AsyncClient,
    it_authenticated_user: User,
    it_authenticated_user_password: str,
) -> None:
    payload = {"current_password": it_authenticated_user_password, "new_password": "x" * (RawPassword.MIN_LEN - 1)}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_400_when_new_password_equals_current(
    it_client: httpx2.AsyncClient,
    it_authenticated_user: User,
    it_authenticated_user_password: str,
) -> None:
    payload = {"current_password": it_authenticated_user_password, "new_password": it_authenticated_user_password}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_401_when_not_authenticated(
    it_client: httpx2.AsyncClient,
) -> None:
    payload = {"current_password": create_raw_password(), "new_password": create_raw_password()}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 401


async def test_returns_403_and_keeps_password_when_current_password_is_wrong(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_user: User,
) -> None:
    old_password_hash = it_authenticated_user.password_hash
    payload = {"current_password": create_raw_password(), "new_password": create_raw_password()}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 403
    await it_session.refresh(it_authenticated_user)
    assert it_authenticated_user.password_hash == old_password_hash
