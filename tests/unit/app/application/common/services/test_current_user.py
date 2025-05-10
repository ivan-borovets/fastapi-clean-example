from unittest.mock import create_autospec

import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user.entity import User


@pytest.mark.asyncio
async def test_get_current_user_success(sample_user: User) -> None:
    identity_provider = create_autospec(IdentityProvider)
    user_gateway = create_autospec(UserCommandGateway)
    user_gateway.read_by_id.return_value = sample_user
    service = CurrentUserService(identity_provider, user_gateway)

    current_user = await service.get_current_user()
    assert current_user == sample_user


@pytest.mark.asyncio
async def test_get_current_user_not_found() -> None:
    identity_provider = create_autospec(IdentityProvider)
    user_gateway = create_autospec(UserCommandGateway)
    user_gateway.read_by_id.return_value = None
    service = CurrentUserService(identity_provider, user_gateway)

    with pytest.raises(AuthorizationError):
        await service.get_current_user()
