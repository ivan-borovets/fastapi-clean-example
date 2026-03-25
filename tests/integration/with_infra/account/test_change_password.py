import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from tests.integration.with_infra.account.constants import CHANGE_PASSWORD_ENDPOINT
from tests.integration.with_infra.authentication import authenticate
from tests.integration.with_infra.factories import create_raw_password, create_user_with_password


async def test_returns_204_and_changes_password(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    it_session.add(user)
    await it_session.commit()
    await authenticate(it_client, user.username.value, password)
    old_password_hash = user.password_hash
    payload = {"current_password": password, "new_password": create_raw_password()}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 204
    await it_session.refresh(user)
    assert user.password_hash != old_password_hash


async def test_returns_400_when_new_password_is_too_short(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    it_session.add(user)
    await it_session.commit()
    await authenticate(it_client, user.username.value, password)
    payload = {"current_password": password, "new_password": "x" * (RawPassword.MIN_LEN - 1)}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_400_when_new_password_equals_current(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    it_session.add(user)
    await it_session.commit()
    await authenticate(it_client, user.username.value, password)
    payload = {"current_password": password, "new_password": password}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_401_when_not_authenticated(
    it_client: httpx.AsyncClient,
) -> None:
    payload = {"current_password": create_raw_password(), "new_password": create_raw_password()}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 401


async def test_returns_403_when_current_password_is_wrong(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    it_session.add(user)
    await it_session.commit()
    await authenticate(it_client, user.username.value, password)
    payload = {"current_password": create_raw_password(), "new_password": create_raw_password()}

    r = await it_client.put(CHANGE_PASSWORD_ENDPOINT, json=payload)

    assert r.status_code == 403
