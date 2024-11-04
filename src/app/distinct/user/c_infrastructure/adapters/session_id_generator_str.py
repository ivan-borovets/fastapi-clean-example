import secrets

from app.distinct.user.b_application.ports.session_id_generator import (
    SessionIdGenerator,
)


class StrSessionIdGenerator(SessionIdGenerator):
    def __call__(self) -> str:
        return secrets.token_urlsafe(32)
