import secrets

from app.outbound.auth_ctx.model import SessionId


def create_session_id(value: str | None = None) -> SessionId:
    return SessionId(value if value is not None else secrets.token_urlsafe(32))
