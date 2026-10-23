import secrets

from app.outbound.auth_ctx.model import SessionId


def create_session_id() -> SessionId:
    return SessionId(secrets.token_urlsafe(32))
