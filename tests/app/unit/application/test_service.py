import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.services.authorization.service import AuthorizationService
from tests.app.unit.application.permission_stubs import (
    AlwaysAllow,
    AlwaysDeny,
    DummyContext,
)


def test_authorize_allows_when_permission_is_satisfied() -> None:
    context = DummyContext()
    permission = AlwaysAllow()
    sut = AuthorizationService()

    sut.authorize(permission, context=context)


def test_authorize_raises_when_permission_not_satisfied() -> None:
    context = DummyContext()
    permission = AlwaysDeny()
    sut = AuthorizationService()

    with pytest.raises(AuthorizationError):
        sut.authorize(permission, context=context)
