from app.core.common.authorization.composite import AnyOf
from tests.unit.core.common.authorization.permission_stubs import AlwaysAllow, AlwaysDeny
from tests.unit.core.common.authorization.types_ import DummyContext


def test_any_of_allows_when_one_allows() -> None:
    sut = AnyOf(AlwaysDeny(), AlwaysAllow())

    assert sut.is_satisfied_by(DummyContext()) is True


def test_any_of_denies_when_all_deny() -> None:
    sut = AnyOf(AlwaysDeny(), AlwaysDeny())

    assert sut.is_satisfied_by(DummyContext()) is False


def test_any_of_denies_when_empty() -> None:
    sut: AnyOf[DummyContext] = AnyOf()

    assert sut.is_satisfied_by(DummyContext()) is False
