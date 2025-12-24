import secrets


class StrAuthSessionIdGenerator:
    def generate(self) -> str:
        return secrets.token_urlsafe(32)
