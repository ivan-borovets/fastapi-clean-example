import httpx2
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from tests.integration.with_infra.factories import create_raw_user_id, create_super_admin, create_user
from tests.integration.with_infra.users.constants import USERS_ENDPOINT


async def test_returns_204_and_revokes_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_super_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, role=UserRole.ADMIN)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/roles/admin/")

    assert r.status_code == 204
    await it_session.refresh(target)
    assert target.role == UserRole.USER


async def test_returns_204_and_keeps_user_role_when_already_user(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_super_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, role=UserRole.USER)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/roles/admin/")

    assert r.status_code == 204
    await it_session.refresh(target)
    assert target.role == UserRole.USER


async def test_returns_401_when_not_authenticated(
    it_client: httpx2.AsyncClient,
) -> None:
    r = await it_client.delete(f"{USERS_ENDPOINT}{create_raw_user_id()}/roles/admin/")

    assert r.status_code == 401


async def test_returns_403_and_keeps_role_when_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, role=UserRole.ADMIN)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/roles/admin/")

    assert r.status_code == 403
    await it_session.refresh(target)
    assert target.role == UserRole.ADMIN


async def test_returns_403_and_keeps_role_when_user(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_user: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, role=UserRole.ADMIN)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/roles/admin/")

    assert r.status_code == 403
    await it_session.refresh(target)
    assert target.role == UserRole.ADMIN


async def test_returns_403_and_keeps_role_when_super_admin_targets_super_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_super_admin: User,
    it_user_service: UserService,
) -> None:
    other_super_admin = create_super_admin(it_user_service)
    it_session.add(other_super_admin)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{other_super_admin.id_}/roles/admin/")

    assert r.status_code == 403
    await it_session.refresh(other_super_admin)
    assert other_super_admin.role == UserRole.SUPER_ADMIN


async def test_returns_404_when_user_not_found(
    it_client: httpx2.AsyncClient,
    it_authenticated_super_admin: User,
) -> None:
    r = await it_client.delete(f"{USERS_ENDPOINT}{create_raw_user_id()}/roles/admin/")

    assert r.status_code == 404
