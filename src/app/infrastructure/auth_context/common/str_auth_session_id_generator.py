import secrets


class StrAuthSessionIdGenerator:
    def __call__(self) -> str:
        return secrets.token_urlsafe(32)
