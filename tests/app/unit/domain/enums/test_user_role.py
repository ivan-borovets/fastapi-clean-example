import pytest

from app.domain.enums.user_role import UserRole


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (UserRole.USER, True),
        (UserRole.ADMIN, True),
        (UserRole.SUPER_ADMIN, False),
    ],
)
def test_assignability(role: UserRole, expected: bool) -> None:
    assert role.is_assignable is expected


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (UserRole.USER, True),
        (UserRole.ADMIN, True),
        (UserRole.SUPER_ADMIN, False),
    ],
)
def test_changeability(role: UserRole, expected: bool) -> None:
    assert role.is_changeable is expected
