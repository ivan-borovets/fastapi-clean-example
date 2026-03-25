import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from app.infrastructure.persistence_sqla.mappings.user import users_table
from tests.integration.with_infra.account.constants import SIGN_UP_ENDPOINT
from tests.integration.with_infra.factories import (
    create_raw_password,
    create_raw_username,
    create_user,
)


async def test_returns_204_and_creates_user(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
) -> None:
    username = create_raw_username()
    password = create_raw_password()
    payload = {"username": username, "password": password}

    r = await it_client.post(SIGN_UP_ENDPOINT, json=payload)

    assert r.status_code == 204
    stmt = select(User).where(users_table.c.username == username)
    user = await it_session.scalar(stmt)
    assert isinstance(user, User)
    assert user.username.value == username
    assert user.role == UserRole.USER
    assert user.is_active is True


async def test_returns_400_when_username_is_too_short(
    it_client: httpx.AsyncClient,
) -> None:
    payload = {"username": "x" * (Username.MIN_LEN - 1), "password": create_raw_password()}

    r = await it_client.post(SIGN_UP_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_400_when_password_is_too_short(
    it_client: httpx.AsyncClient,
) -> None:
    payload = {"username": create_raw_username(), "password": "x" * (RawPassword.MIN_LEN - 1)}

    r = await it_client.post(SIGN_UP_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_409_when_username_already_exists(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    username = create_raw_username()
    user = create_user(it_user_service, raw_username=username)
    it_session.add(user)
    await it_session.commit()
    payload = {"username": username, "password": create_raw_password()}

    r = await it_client.post(SIGN_UP_ENDPOINT, json=payload)

    assert r.status_code == 409
    stmt = select(func.count()).select_from(User)
    count = await it_session.scalar(stmt)
    assert count == 1
