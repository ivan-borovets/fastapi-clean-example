from datetime import timedelta

import httpx2
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
    it_client: httpx2.AsyncClient,
    it_authenticated_admin: User,
) -> None:
    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 200
    body = r.json()
    users = body["users"]
    assert len(users) == 1
    user = users[0]
    assert user["id"] == str(it_authenticated_admin.id_)
    assert user["username"] == it_authenticated_admin.username.value
    assert user["role"] == it_authenticated_admin.role
    assert user["is_active"] is it_authenticated_admin.is_active
    assert body["total"] == 1


async def test_returns_200_and_applies_default_pagination(
    it_client: httpx2.AsyncClient,
    it_authenticated_admin: User,
) -> None:
    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 20
    assert body["offset"] == 0


async def test_returns_200_and_empty_page_when_offset_exceeds_total(
    it_client: httpx2.AsyncClient,
    it_authenticated_admin: User,
) -> None:
    r = await it_client.get(USERS_ENDPOINT, params={"offset": 1})

    assert r.status_code == 200
    body = r.json()
    assert body["users"] == []
    assert body["total"] == 1


async def test_returns_200_and_respects_pagination_params(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    users = [create_user(it_user_service) for _ in range(4)]
    it_session.add_all(users)
    await it_session.commit()

    r = await it_client.get(USERS_ENDPOINT, params={"limit": 2, "offset": 1})

    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    assert body["limit"] == 2
    assert body["offset"] == 1
    assert len(body["users"]) == 2


async def test_returns_200_and_sorts_by_updated_at_desc(
    it_client: httpx2.AsyncClient,
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
    await authenticate(it_client, username=admin.username.value, password=admin_password)

    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 200
    body = r.json()
    first, second, third = body["users"]
    assert first["id"] == str(admin.id_)
    assert second["id"] == str(user_2.id_)
    assert third["id"] == str(user_1.id_)


async def test_returns_200_and_sorts_by_username_asc(
    it_client: httpx2.AsyncClient,
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
    await authenticate(it_client, username=admin.username.value, password=admin_password)

    r = await it_client.get(USERS_ENDPOINT, params={"sorting_field": "username", "sorting_order": "asc"})

    assert r.status_code == 200
    body = r.json()
    first, second, third = body["users"]
    assert first["username"] == admin.username.value
    assert second["username"] == user_2.username.value
    assert third["username"] == user_1.username.value


async def test_returns_401_when_not_authenticated(
    it_client: httpx2.AsyncClient,
) -> None:
    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 401


async def test_returns_403_when_user(
    it_client: httpx2.AsyncClient,
    it_authenticated_user: User,
) -> None:
    r = await it_client.get(USERS_ENDPOINT)

    assert r.status_code == 403
