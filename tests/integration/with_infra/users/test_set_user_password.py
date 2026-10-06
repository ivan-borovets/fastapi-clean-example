import httpx2
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from tests.integration.with_infra.factories import (
    create_password,
    create_raw_password,
    create_raw_user_id,
    create_super_admin,
    create_user,
)
from tests.integration.with_infra.users.constants import USERS_ENDPOINT


async def test_returns_204_and_sets_password(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service)
    it_session.add(target)
    await it_session.commit()
    password = create_raw_password()
    payload = {"password": password}

    r = await it_client.put(f"{USERS_ENDPOINT}{target.id_}/password/", json=payload)

    assert r.status_code == 204
    await it_session.refresh(target)
    is_password_valid = await it_user_service.is_password_valid(target, create_password(password))
    assert is_password_valid is True


async def test_returns_204_and_sets_admin_password_when_super_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_super_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, role=UserRole.ADMIN)
    it_session.add(target)
    await it_session.commit()
    password = create_raw_password()
    payload = {"password": password}

    r = await it_client.put(f"{USERS_ENDPOINT}{target.id_}/password/", json=payload)

    assert r.status_code == 204
    await it_session.refresh(target)
    is_password_valid = await it_user_service.is_password_valid(target, create_password(password))
    assert is_password_valid is True


async def test_returns_400_when_password_is_too_short(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service)
    it_session.add(target)
    await it_session.commit()
    payload = {"password": "x" * (RawPassword.MIN_LEN - 1)}

    r = await it_client.put(f"{USERS_ENDPOINT}{target.id_}/password/", json=payload)

    assert r.status_code == 400


async def test_returns_401_when_not_authenticated(
    it_client: httpx2.AsyncClient,
) -> None:
    payload = {"password": create_raw_password()}

    r = await it_client.put(f"{USERS_ENDPOINT}{create_raw_user_id()}/password/", json=payload)

    assert r.status_code == 401


async def test_returns_403_and_keeps_password_when_user(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_user: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service)
    it_session.add(target)
    await it_session.commit()
    old_password_hash = target.password_hash
    payload = {"password": create_raw_password()}

    r = await it_client.put(f"{USERS_ENDPOINT}{target.id_}/password/", json=payload)

    assert r.status_code == 403
    await it_session.refresh(target)
    assert target.password_hash == old_password_hash


async def test_returns_403_and_keeps_password_when_admin_targets_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    other_admin = create_user(it_user_service, role=UserRole.ADMIN)
    it_session.add(other_admin)
    await it_session.commit()
    old_password_hash = other_admin.password_hash
    payload = {"password": create_raw_password()}

    r = await it_client.put(f"{USERS_ENDPOINT}{other_admin.id_}/password/", json=payload)

    assert r.status_code == 403
    await it_session.refresh(other_admin)
    assert other_admin.password_hash == old_password_hash


async def test_returns_403_and_keeps_password_when_super_admin_targets_super_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_super_admin: User,
    it_user_service: UserService,
) -> None:
    other_super_admin = create_super_admin(it_user_service)
    it_session.add(other_super_admin)
    await it_session.commit()
    old_password_hash = other_super_admin.password_hash
    payload = {"password": create_raw_password()}

    r = await it_client.put(f"{USERS_ENDPOINT}{other_super_admin.id_}/password/", json=payload)

    assert r.status_code == 403
    await it_session.refresh(other_super_admin)
    assert other_super_admin.password_hash == old_password_hash


async def test_returns_404_when_user_not_found(
    it_client: httpx2.AsyncClient,
    it_authenticated_admin: User,
) -> None:
    payload = {"password": create_raw_password()}

    r = await it_client.put(f"{USERS_ENDPOINT}{create_raw_user_id()}/password/", json=payload)

    assert r.status_code == 404
