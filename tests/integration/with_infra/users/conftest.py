import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from tests.integration.with_infra.authentication import authenticate
from tests.integration.with_infra.factories import (
    create_raw_password,
    create_super_admin_with_password,
    create_user_with_password,
)


@pytest.fixture
async def it_admin(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> User:
    password = create_raw_password()
    admin = await create_user_with_password(it_user_service, raw_password=password, role=UserRole.ADMIN)
    it_session.add(admin)
    await it_session.commit()
    await authenticate(it_client, admin.username.value, password)
    return admin


@pytest.fixture
async def it_super_admin(
    it_client: httpx.AsyncClient,
    it_session: AsyncSession,
    it_user_service: UserService,
) -> User:
    password = create_raw_password()
    super_admin = await create_super_admin_with_password(it_user_service, raw_password=password)
    it_session.add(super_admin)
    await it_session.commit()
    await authenticate(it_client, super_admin.username.value, password)
    return super_admin
