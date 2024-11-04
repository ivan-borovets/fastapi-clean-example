from datetime import datetime, timedelta
from uuid import UUID

import pytest

from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.entity_user import User


@pytest.fixture
def sample_session() -> Session:
    session_id: str = "session_id"
    user_id: UUID = UUID("12345678-1234-5678-1234-567812345678")
    expiration: datetime = datetime.now() + timedelta(days=1)
    return Session.create(session_id=session_id, user_id=user_id, expiration=expiration)


@pytest.fixture
def sample_user() -> User:
    user_id: UUID = UUID("12345678-1234-5678-1234-567812345678")
    username: str = "username"
    password_hash: bytes = bytes.fromhex("123456789abcdef0")
    return User.create(user_id=user_id, username=username, password_hash=password_hash)
