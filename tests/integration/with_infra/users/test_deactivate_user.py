import httpx2
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.outbound.auth_ctx.model import AuthSession
from app.outbound.persistence_sqla.mappings.auth_session import auth_sessions_table
from tests.integration.with_infra.factories import (
    create_auth_session,
    create_raw_user_id,
    create_super_admin,
    create_user,
)
from tests.integration.with_infra.users.constants import USERS_ENDPOINT


async def test_returns_204_and_deactivates_user(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, is_active=True)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 204
    await it_session.refresh(target)
    assert target.is_active is False


async def test_returns_204_and_revokes_target_sessions(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, is_active=True)
    it_session.add(target)
    await it_session.flush()
    it_session.add(create_auth_session(raw_user_id=target.id_))
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 204
    stmt = select(func.count()).select_from(AuthSession).where(auth_sessions_table.c.user_id == target.id_)
    count = await it_session.scalar(stmt)
    assert count == 0


async def test_returns_204_and_keeps_user_inactive_when_already_inactive(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, is_active=False)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 204
    await it_session.refresh(target)
    assert target.is_active is False


async def test_returns_204_and_deactivates_admin_when_super_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_super_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, role=UserRole.ADMIN, is_active=True)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 204
    await it_session.refresh(target)
    assert target.is_active is False


async def test_returns_401_when_not_authenticated(
    it_client: httpx2.AsyncClient,
) -> None:
    r = await it_client.delete(f"{USERS_ENDPOINT}{create_raw_user_id()}/activation/")

    assert r.status_code == 401


async def test_returns_403_and_keeps_activation_when_user(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_user: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, is_active=True)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 403
    await it_session.refresh(target)
    assert target.is_active is True


async def test_returns_403_and_keeps_activation_when_admin_targets_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_admin: User,
    it_user_service: UserService,
) -> None:
    other_admin = create_user(it_user_service, role=UserRole.ADMIN)
    it_session.add(other_admin)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{other_admin.id_}/activation/")

    assert r.status_code == 403
    await it_session.refresh(other_admin)
    assert other_admin.is_active is True


async def test_returns_403_and_keeps_activation_when_super_admin_targets_super_admin(
    it_client: httpx2.AsyncClient,
    it_session: AsyncSession,
    it_authenticated_super_admin: User,
    it_user_service: UserService,
) -> None:
    other_super_admin = create_super_admin(it_user_service)
    it_session.add(other_super_admin)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{other_super_admin.id_}/activation/")

    assert r.status_code == 403
    await it_session.refresh(other_super_admin)
    assert other_super_admin.is_active is True


async def test_returns_404_when_user_not_found(
    it_client: httpx2.AsyncClient,
    it_authenticated_admin: User,
) -> None:
    r = await it_client.delete(f"{USERS_ENDPOINT}{create_raw_user_id()}/activation/")

    assert r.status_code == 404
