import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from tests.integration.with_infra.authentication import authenticate
from tests.integration.with_infra.factories import (
    create_raw_password,
    create_raw_username,
    create_user,
    create_user_with_password,
)
from tests.integration.with_infra.users.constants import USERS_ENDPOINT


async def test_returns_201_and_creates_user(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_admin: User,
) -> None:
    username = create_raw_username()
    payload = {"username": username, "password": create_raw_password(), "role": "user"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 201
    body = r.json()
    assert "created_at" in body
    user = await it_session.get(User, body["id"])
    assert isinstance(user, User)
    assert user.username.value == username
    assert user.role == UserRole.USER
    assert user.is_active is True


async def test_returns_201_and_super_admin_creates_admin(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_super_admin: User,
) -> None:
    username = create_raw_username()
    payload = {"username": username, "password": create_raw_password(), "role": "admin"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 201
    body = r.json()
    user = await it_session.get(User, body["id"])
    assert isinstance(user, User)
    assert user.role == UserRole.ADMIN


async def test_returns_400_when_username_is_too_short(
    it_client: httpx.AsyncClient,
    it_admin: User,
) -> None:
    payload = {"username": "x" * (Username.MIN_LEN - 1), "password": create_raw_password(), "role": "user"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_400_when_password_is_too_short(
    it_client: httpx.AsyncClient,
    it_admin: User,
) -> None:
    payload = {"username": create_raw_username(), "password": "x" * (RawPassword.MIN_LEN - 1), "role": "user"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 400


async def test_returns_401_when_not_authenticated(
    it_client: httpx.AsyncClient,
) -> None:
    payload = {"username": create_raw_username(), "password": create_raw_password(), "role": "user"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 401


async def test_returns_403_when_user_role(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    it_session.add(user)
    await it_session.commit()
    await authenticate(it_client, user.username.value, password)
    payload = {"username": create_raw_username(), "password": create_raw_password(), "role": "user"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 403


async def test_returns_403_when_admin_creates_admin(
    it_client: httpx.AsyncClient,
    it_admin: User,
) -> None:
    payload = {"username": create_raw_username(), "password": create_raw_password(), "role": "admin"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 403


async def test_returns_409_when_username_already_exists(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_admin: User,
    it_user_service: UserService,
) -> None:
    username = create_raw_username()
    existing = create_user(it_user_service, raw_username=username)
    it_session.add(existing)
    await it_session.commit()
    payload = {"username": username, "password": create_raw_password(), "role": "user"}

    r = await it_client.post(USERS_ENDPOINT, json=payload)

    assert r.status_code == 409
    count = await it_session.scalar(select(func.count()).select_from(User))
    assert count == 2
