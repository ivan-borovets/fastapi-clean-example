from datetime import timedelta

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from tests.integration.with_infra.authentication import authenticate
from tests.integration.with_infra.factories import (
    create_raw_now,
    create_raw_password,
    create_user,
    create_user_with_password,
)
from tests.integration.with_infra.users.constants import USERS_ENDPOINT


async def test_returns_200_and_lists_single_user(
    it_client: httpx.AsyncClient,
    it_admin: User,
) -> None:
    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 200
    payload = r.json()
    users = payload["users"]
    assert len(users) == 1
    assert users[0]["id"] == str(it_admin.id_)
    assert payload["total"] == 1
    assert payload["limit"] == 20
    assert payload["offset"] == 0


async def test_returns_200_and_lists_multiple_users(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_admin: User,
    it_user_service: UserService,
) -> None:
    user_1 = create_user(it_user_service)
    user_2 = create_user(it_user_service)
    it_session.add_all([user_1, user_2])
    await it_session.commit()

    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 200
    payload = r.json()
    assert payload["total"] == 3
    assert len(payload["users"]) == 3


async def test_returns_200_and_respects_pagination_params(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_admin: User,
    it_user_service: UserService,
) -> None:
    users = [create_user(it_user_service) for _ in range(4)]
    it_session.add_all(users)
    await it_session.commit()

    r = await it_client.get(USERS_ENDPOINT, params={"limit": 2, "offset": 1})

    assert r.status_code == 200
    payload = r.json()
    assert payload["total"] == 5
    assert payload["limit"] == 2
    assert payload["offset"] == 1
    assert len(payload["users"]) == 2


async def test_returns_200_and_sorts_by_updated_at_desc(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    now = create_raw_now()
    admin_password = create_raw_password()
    admin = await create_user_with_password(
        it_user_service, raw_password=admin_password, role=UserRole.ADMIN, raw_now=now
    )
    user_1 = create_user(it_user_service, raw_now=now - timedelta(hours=2))
    user_2 = create_user(it_user_service, raw_now=now - timedelta(hours=1))
    it_session.add_all([admin, user_1, user_2])
    await it_session.commit()
    await authenticate(it_client, admin.username.value, admin_password)

    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 200
    payload = r.json()
    users = payload["users"]
    assert users[0]["id"] == str(admin.id_)
    assert users[1]["id"] == str(user_2.id_)
    assert users[2]["id"] == str(user_1.id_)


async def test_returns_200_and_sorts_by_username_asc(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    admin_password = create_raw_password()
    admin = await create_user_with_password(
        it_user_service, raw_password=admin_password, role=UserRole.ADMIN, raw_username="alice1"
    )
    user_1 = create_user(it_user_service, raw_username="carol1")
    user_2 = create_user(it_user_service, raw_username="bob001")
    it_session.add_all([admin, user_1, user_2])
    await it_session.commit()
    await authenticate(it_client, admin.username.value, admin_password)

    r = await it_client.get(USERS_ENDPOINT, params={"sorting_field": "username", "sorting_order": "ASC"})

    assert r.status_code == 200
    payload = r.json()
    users = payload["users"]
    assert users[0]["username"] == admin.username.value
    assert users[1]["username"] == user_2.username.value
    assert users[2]["username"] == user_1.username.value


async def test_returns_401_when_not_authenticated(
    it_client: httpx.AsyncClient,
) -> None:
    r = await it_client.get(USERS_ENDPOINT)

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

    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 403
