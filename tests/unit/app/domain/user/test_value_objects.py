import pytest

from app.domain.user.exceptions.base import DomainFieldError
from app.domain.user.value_objects import Username, RawPassword

from app.domain.user.validation.constants import (
    PATTERN_START,
    PATTERN_ALLOWED_CHARS,
    PATTERN_NO_CONSECUTIVE_SPECIALS,
    PATTERN_END,
    USERNAME_MIN_LEN,
    USERNAME_MAX_LEN, PASSWORD_MIN_LEN,
)

valid_usernames_with_length: list[str] = [
    "a" * USERNAME_MIN_LEN,
    "a" * USERNAME_MAX_LEN,
]

invalid_usernames_with_length: list[str] = [
    "a" * (USERNAME_MIN_LEN - 1),
    "a" * (USERNAME_MAX_LEN + 1),
]

valid_raw_password_with_length: list[str] = ["a" * PASSWORD_MIN_LEN, ]
invalid_raw_password_with_length: list[str] = ["a" * (PASSWORD_MIN_LEN - 1), ]



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
def test_valid_usernames_with_length(username):
    assert USERNAME_MIN_LEN <= len(username) <= USERNAME_MAX_LEN


@pytest.mark.parametrize("username", invalid_usernames_with_length)
def test_invalid_usernames_with_length(username):
    assert len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN


@pytest.mark.parametrize("username", valid_usernames)
def test_valid_usernames(username):
    assert PATTERN_START.match(username)
    assert PATTERN_ALLOWED_CHARS.fullmatch(username)
    assert PATTERN_NO_CONSECUTIVE_SPECIALS.fullmatch(username)
    assert PATTERN_END.match(username)


@pytest.mark.parametrize("username", invalid_usernames)
def test_invalid_usernames(username):
    assert not (
        PATTERN_START.match(username)
        and PATTERN_ALLOWED_CHARS.fullmatch(username)
        and PATTERN_NO_CONSECUTIVE_SPECIALS.match(username)
        and PATTERN_END.match(username)
    )


@pytest.mark.parametrize("username", valid_usernames_with_length)
def test_vo_username_valid_length(username):
    Username(username)


@pytest.mark.parametrize("username", invalid_usernames_with_length)
def test_vo_username_invalid_length(username):
    with pytest.raises(DomainFieldError):
        Username(username)


@pytest.mark.parametrize("username", valid_usernames)
def test_vo_username_valid_pattern(username):
    Username(username)


@pytest.mark.parametrize("username", invalid_usernames)
def test_vo_username_invalid_pattern(username):
    with pytest.raises(DomainFieldError):
        Username(username)

@pytest.mark.parametrize("password", valid_raw_password_with_length)
def test_vo_raw_password_valid_length(password):
    RawPassword(password)

@pytest.mark.parametrize("password", invalid_raw_password_with_length)
def test_vo_raw_password_valid_length(password):
    with pytest.raises(DomainFieldError):
        RawPassword(password)