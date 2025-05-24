from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.raw_password.constants import PASSWORD_MIN_LEN


def validate_password_length(password_value: str) -> None:
    if len(password_value) < PASSWORD_MIN_LEN:
        raise DomainFieldError(
            f"Password must be at least {PASSWORD_MIN_LEN} characters long.",
        )
