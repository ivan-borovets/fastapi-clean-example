import pytest

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.username.constants import (
    USERNAME_MAX_LEN,
    USERNAME_MIN_LEN,
)
from app.domain.value_objects.username.username import Username


@pytest.mark.parametrize(
    ("username", "expected_exception"),
    [
        pytest.param("a" * USERNAME_MIN_LEN, None, id="min_len"),
        pytest.param("a" * USERNAME_MAX_LEN, None, id="max_len"),
        pytest.param("a" * (USERNAME_MIN_LEN - 1), DomainFieldError, id="lt_min"),
        pytest.param("a" * (USERNAME_MAX_LEN + 1), DomainFieldError, id="gt_max"),
    ],
)
def test_vo_username_length(username, expected_exception):
    if not expected_exception:
        Username(username)

    else:
        with pytest.raises(expected_exception):
            Username(username)


@pytest.mark.parametrize(
    ("username", "expected_exception"),
    [
        ("username", None),
        ("user.name", None),
        ("user-name", None),
        ("user_name", None),
        ("user123", None),
        ("user.name123", None),
        ("u.ser-name123", None),
        ("u-ser_name", None),
        ("u-ser.name", None),
        (".username", DomainFieldError),
        ("-username", DomainFieldError),
        ("_username", DomainFieldError),
        ("username.", DomainFieldError),
        ("username-", DomainFieldError),
        ("username_", DomainFieldError),
        ("user..name", DomainFieldError),
        ("user--name", DomainFieldError),
        ("user__name", DomainFieldError),
        ("user!name", DomainFieldError),
        ("user@name", DomainFieldError),
        ("user#name", DomainFieldError),
    ],
)
def test_vo_username_correctness(username, expected_exception):
    if not expected_exception:
        Username(username)

    else:
        with pytest.raises(expected_exception):
            Username(username)
