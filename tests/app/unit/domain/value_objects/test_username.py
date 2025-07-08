import pytest

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.username.constants import (
    USERNAME_MAX_LEN,
    USERNAME_MIN_LEN,
)
from app.domain.value_objects.username.username import Username


@pytest.mark.parametrize(
    "username",
    [
        pytest.param("a" * USERNAME_MIN_LEN, id="min_len"),
        pytest.param("a" * USERNAME_MAX_LEN, id="max_len"),
    ],
)
def test_accepts_boundary_length(username: str) -> None:
    Username(username)


@pytest.mark.parametrize(
    "username",
    [
        pytest.param("a" * (USERNAME_MIN_LEN - 1), id="too_small_len"),
        pytest.param("a" * (USERNAME_MAX_LEN + 1), id="too_big_len"),
    ],
)
def test_rejects_out_of_bounds_length(username: str) -> None:
    with pytest.raises(DomainFieldError):
        Username(username)


@pytest.mark.parametrize(
    "username",
    [
        "username",
        "user.name",
        "user-name",
        "user_name",
        "user123",
        "user.name123",
        "u.ser-name123",
        "u-ser_name",
        "u-ser.name",
    ],
)
def test_accepts_correct_names(username: str) -> None:
    Username(username)


@pytest.mark.parametrize(
    "username",
    [
        ".username",
        "-username",
        "_username",
        "username.",
        "username-",
        "username_",
        "user..name",
        "user--name",
        "user__name",
        "user!name",
        "user@name",
        "user#name",
    ],
)
def test_rejects_incorrect_names(username: str) -> None:
    with pytest.raises(DomainFieldError):
        Username(username)
