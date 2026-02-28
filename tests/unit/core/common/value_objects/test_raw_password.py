import pytest

from app.core.common.exceptions import BusinessTypeError
from app.core.common.value_objects.raw_password import RawPassword


def test_accepts_boundary_length() -> None:
    password = "a" * RawPassword.MIN_LEN

    RawPassword(password)


def test_rejects_out_of_bounds_length() -> None:
    password = "a" * (RawPassword.MIN_LEN - 1)

    with pytest.raises(BusinessTypeError):
        RawPassword(password)
