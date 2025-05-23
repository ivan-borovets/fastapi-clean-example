import re

from app.domain.entities.user.validation.constants import (
    PASSWORD_MIN_LEN,
    PATTERN_ALLOWED_CHARS,
    PATTERN_END,
    PATTERN_NO_CONSECUTIVE_SPECIALS,
    PATTERN_START,
    USERNAME_MAX_LEN,
    USERNAME_MIN_LEN,
)
from app.domain.exceptions.base import DomainFieldError


def validate_username_length(username_value: str) -> None:
    if len(username_value) < USERNAME_MIN_LEN or len(username_value) > USERNAME_MAX_LEN:
        raise DomainFieldError(
            f"Username must be between "
            f"{USERNAME_MIN_LEN} and "
            f"{USERNAME_MAX_LEN} characters.",
        )


def validate_username_pattern(username_value: str) -> None:
    """
    :raises DomainFieldError:
    """
    if not re.match(PATTERN_START, username_value):
        raise DomainFieldError(
            "Username must start with a letter (A-Z, a-z) or a digit (0-9).",
        )
    if not re.fullmatch(PATTERN_ALLOWED_CHARS, username_value):
        raise DomainFieldError(
            "Username can only contain letters (A-Z, a-z), digits (0-9), "
            "dots (.), hyphens (-), and underscores (_).",
        )
    if not re.fullmatch(PATTERN_NO_CONSECUTIVE_SPECIALS, username_value):
        raise DomainFieldError(
            "Username cannot contain consecutive special characters"
            " like .., --, or __.",
        )
    if not re.match(PATTERN_END, username_value):
        raise DomainFieldError(
            "Username must end with a letter (A-Z, a-z) or a digit (0-9).",
        )


def validate_password_length(password_value: str) -> None:
    if len(password_value) < PASSWORD_MIN_LEN:
        raise DomainFieldError(
            f"Password must be at least {PASSWORD_MIN_LEN} characters long.",
        )
