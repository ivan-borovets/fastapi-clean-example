from uuid import UUID

import pytest

from app.domain.user.entity_user import User


@pytest.fixture
def sample_user() -> User:
    user_id: UUID = UUID("12345678-1234-5678-1234-567812345678")
    username: str = "username"
    password_hash: bytes = bytes.fromhex("123456789abcdef0")
    return User.create(user_id=user_id, username=username, password_hash=password_hash)
