import pytest

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.raw_password.constants import PASSWORD_MIN_LEN
from app.domain.value_objects.raw_password.raw_password import RawPassword


def test_accepts_boundary_length() -> None:
    password = "a" * PASSWORD_MIN_LEN

    RawPassword(password)


def test_rejects_out_of_bounds_length() -> None:
    password = "a" * (PASSWORD_MIN_LEN - 1)

    with pytest.raises(DomainFieldError):
        RawPassword(password)
