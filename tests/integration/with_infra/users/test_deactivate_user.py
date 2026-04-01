import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from tests.integration.with_infra.authentication import authenticate
from tests.integration.with_infra.factories import (
    create_raw_password,
    create_raw_user_id,
    create_user,
    create_user_with_password,
)
from tests.integration.with_infra.users.constants import USERS_ENDPOINT


async def test_returns_204_and_deactivates_user(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, is_active=True)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 204
    await it_session.refresh(target)
    assert target.is_active is False


async def test_returns_204_when_user_already_inactive(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_admin: User,
    it_user_service: UserService,
) -> None:
    target = create_user(it_user_service, is_active=False)
    it_session.add(target)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 204
    await it_session.refresh(target)
    assert target.is_active is False


async def test_returns_401_when_not_authenticated(
    it_client: httpx.AsyncClient,
) -> None:
    r = await it_client.delete(f"{USERS_ENDPOINT}{create_raw_user_id()}/activation/")

    assert r.status_code == 401


async def test_returns_403_when_user_role(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> None:
    password = create_raw_password()
    user = await create_user_with_password(it_user_service, raw_password=password)
    target = create_user(it_user_service, is_active=True)
    it_session.add_all([user, target])
    await it_session.commit()
    await authenticate(it_client, user.username.value, password)

    r = await it_client.delete(f"{USERS_ENDPOINT}{target.id_}/activation/")

    assert r.status_code == 403


async def test_returns_403_when_admin_targets_admin(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_admin: User,
    it_user_service: UserService,
) -> None:
    other_admin = create_user(it_user_service, role=UserRole.ADMIN)
    it_session.add(other_admin)
    await it_session.commit()

    r = await it_client.delete(f"{USERS_ENDPOINT}{other_admin.id_}/activation/")

    assert r.status_code == 403


async def test_returns_404_when_user_not_found(
    it_client: httpx.AsyncClient,
    it_admin: User,
) -> None:
    r = await it_client.delete(f"{USERS_ENDPOINT}{create_raw_user_id()}/activation/")

    assert r.status_code == 404
