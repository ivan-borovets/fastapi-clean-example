from app.application.common.services.authorization.composite import AnyOf
from tests.app.unit.application.authz_service.permission_stubs import (
    AlwaysAllow,
    AlwaysDeny,
    DummyContext,
)


def test_any_of_allows_if_at_least_one_allows() -> None:
    sut = AnyOf(AlwaysDeny(), AlwaysAllow())
    assert sut.is_satisfied_by(DummyContext())


def test_any_of_denies_if_all_deny() -> None:
    sut = AnyOf(AlwaysDeny(), AlwaysDeny())
    assert not sut.is_satisfied_by(DummyContext())


def test_any_of_empty_returns_false() -> None:
    sut: AnyOf[DummyContext] = AnyOf()
    assert not sut.is_satisfied_by(DummyContext())
