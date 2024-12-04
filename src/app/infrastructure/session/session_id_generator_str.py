import secrets


class StrSessionIdGenerator:
    def __call__(self) -> str:
        return secrets.token_urlsafe(32)
