import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from tests.integration.with_infra.account.constants import LOG_IN_ENDPOINT
from tests.integration.with_infra.factories import (
    create_raw_password,
    create_raw_username,
    create_user_with_password,
)


async def test_returns_204_and_sets_cookie(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    it_session.add(user)
    await it_session.commit()
    payload = {"username": user.username.value, "password": password}

    r = await it_client.post(LOG_IN_ENDPOINT, json=payload)

    assert r.status_code == 204
    assert "auth_token" in r.cookies


async def test_returns_400_when_username_is_too_short(
    it_client: httpx.AsyncClient,
) -> None:
    payload = {"username": "x" * (Username.MIN_LEN - 1), "password": create_raw_password()}

    r = await it_client.post(LOG_IN_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_400_when_password_is_too_short(
    it_client: httpx.AsyncClient,
) -> None:
    payload = {"username": create_raw_username(), "password": "x" * (RawPassword.MIN_LEN - 1)}

    r = await it_client.post(LOG_IN_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_401_when_user_does_not_exist(
    it_client: httpx.AsyncClient,
) -> None:
    payload = {"username": create_raw_username(), "password": create_raw_password()}

    r = await it_client.post(LOG_IN_ENDPOINT, json=payload)

    assert r.status_code == 401


async def test_returns_401_when_password_is_wrong(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    user = await create_user_with_password(it_user_service)
    it_session.add(user)
    await it_session.commit()
    payload = {"username": user.username.value, "password": create_raw_password()}

    r = await it_client.post(LOG_IN_ENDPOINT, json=payload)

    assert r.status_code == 401


async def test_returns_401_when_user_is_inactive(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password, is_active=False)
    it_session.add(user)
    await it_session.commit()
    payload = {"username": user.username.value, "password": password}

    r = await it_client.post(LOG_IN_ENDPOINT, json=payload)

    assert r.status_code == 401
