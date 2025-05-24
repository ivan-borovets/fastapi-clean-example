import pytest

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.raw_password.constants import PASSWORD_MIN_LEN
from app.domain.value_objects.raw_password.raw_password import RawPassword

valid_raw_password_with_length: list[str] = [
    "a" * PASSWORD_MIN_LEN,
]
invalid_raw_password_with_length: list[str] = [
    "a" * (PASSWORD_MIN_LEN - 1),
]


@pytest.mark.parametrize("password", valid_raw_password_with_length)
def test_vo_raw_password_valid_length(password: str) -> None:
    RawPassword(password)


@pytest.mark.parametrize("password", invalid_raw_password_with_length)
def test_vo_raw_password_invalid_length(password: str) -> None:
    with pytest.raises(DomainFieldError):
        RawPassword(password)
