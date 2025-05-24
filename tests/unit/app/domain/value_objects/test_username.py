import pytest

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.username.constants import (
    PATTERN_ALLOWED_CHARS,
    PATTERN_END,
    PATTERN_NO_CONSECUTIVE_SPECIALS,
    PATTERN_START,
    USERNAME_MAX_LEN,
    USERNAME_MIN_LEN,
)
from app.domain.value_objects.username.username import Username

valid_usernames_with_length: list[str] = [
    "a" * USERNAME_MIN_LEN,
    "a" * USERNAME_MAX_LEN,
]
invalid_usernames_with_length: list[str] = [
    "a" * (USERNAME_MIN_LEN - 1),
    "a" * (USERNAME_MAX_LEN + 1),
]
valid_usernames: list[str] = [
    "username",
    "user.name",
    "user-name",
    "user_name",
    "user123",
    "user.name123",
    "u.ser-name123",
    "u-ser_name",
    "u-ser.name",
]
invalid_usernames: list[str] = [
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
]


@pytest.mark.parametrize("username", valid_usernames_with_length)
def test_valid_usernames_with_length(username: str) -> None:
    assert USERNAME_MIN_LEN <= len(username) <= USERNAME_MAX_LEN


@pytest.mark.parametrize("username", invalid_usernames_with_length)
def test_invalid_usernames_with_length(username: str) -> None:
    assert len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN


@pytest.mark.parametrize("username", valid_usernames)
def test_valid_usernames(username: str) -> None:
    assert PATTERN_START.match(username)
    assert PATTERN_ALLOWED_CHARS.fullmatch(username)
    assert PATTERN_NO_CONSECUTIVE_SPECIALS.fullmatch(username)
    assert PATTERN_END.match(username)


@pytest.mark.parametrize("username", invalid_usernames)
def test_invalid_usernames(username: str) -> None:
    assert not (
        PATTERN_START.match(username)
        and PATTERN_ALLOWED_CHARS.fullmatch(username)
        and PATTERN_NO_CONSECUTIVE_SPECIALS.match(username)
        and PATTERN_END.match(username)
    )


@pytest.mark.parametrize("username", valid_usernames_with_length)
def test_vo_username_valid_length(username: str) -> None:
    Username(username)


@pytest.mark.parametrize("username", invalid_usernames_with_length)
def test_vo_username_invalid_length(username: str) -> None:
    with pytest.raises(DomainFieldError):
        Username(username)


@pytest.mark.parametrize("username", valid_usernames)
def test_vo_username_valid_pattern(username: str) -> None:
    Username(username)


@pytest.mark.parametrize("username", invalid_usernames)
def test_vo_username_invalid_pattern(username: str) -> None:
    with pytest.raises(DomainFieldError):
        Username(username)
