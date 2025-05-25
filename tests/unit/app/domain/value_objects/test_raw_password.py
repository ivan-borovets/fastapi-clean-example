import pytest

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.raw_password.constants import PASSWORD_MIN_LEN
from app.domain.value_objects.raw_password.raw_password import RawPassword


@pytest.mark.parametrize("password", ["a" * PASSWORD_MIN_LEN])
def test_vo_raw_password_valid_length(password):
    RawPassword(password)


@pytest.mark.parametrize("password", ["a" * (PASSWORD_MIN_LEN - 1)])
def test_vo_raw_password_invalid_length(password: str) -> None:
    with pytest.raises(DomainFieldError):
        RawPassword(password)
