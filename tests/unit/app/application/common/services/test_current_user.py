from unittest.mock import create_autospec

import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user import User


@pytest.mark.asyncio
async def test_get_current_user_success(sample_user: User) -> None:
    identity_provider = create_autospec(IdentityProvider)
    user_gateway = create_autospec(UserCommandGateway)
    access_revoker = create_autospec(AccessRevoker)
    user_gateway.read_by_id.return_value = sample_user
    service = CurrentUserService(identity_provider, user_gateway, access_revoker)

    current_user = await service.get_current_user()

    assert current_user == sample_user
    access_revoker.remove_all_user_access.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_not_found() -> None:
    identity_provider = create_autospec(IdentityProvider)
    user_gateway = create_autospec(UserCommandGateway)
    access_revoker = create_autospec(AccessRevoker)

    fake_user_id = "user-123"
    identity_provider.get_current_user_id.return_value = fake_user_id
    user_gateway.read_by_id.return_value = None

    service = CurrentUserService(identity_provider, user_gateway, access_revoker)

    with pytest.raises(AuthorizationError):
        await service.get_current_user()

    access_revoker.remove_all_user_access.assert_awaited_once_with(fake_user_id)
