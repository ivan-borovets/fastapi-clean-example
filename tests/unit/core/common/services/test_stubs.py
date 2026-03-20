import pytest

from tests.unit.core.common.services.factories import create_raw_password
from tests.unit.core.common.services.stubs import StubPasswordHasher


@pytest.mark.asyncio
async def test_stub_password_hasher_verify_true_and_false() -> None:
    raw_ok = create_raw_password("test-password")
    raw_bad = create_raw_password("wrong-password")
    sut = StubPasswordHasher()

    hashed_ok = await sut.hash(raw_ok)

    assert await sut.verify(raw_ok, hashed_ok) is True
    assert await sut.verify(raw_bad, hashed_ok) is False


@pytest.mark.asyncio
async def test_stub_password_hasher_hash_is_deterministic() -> None:
    raw1 = create_raw_password()
    raw2 = create_raw_password()
    sut = StubPasswordHasher()

    h1a = await sut.hash(raw1)
    h1b = await sut.hash(raw1)
    h2 = await sut.hash(raw2)

    assert h1a == h1b
    assert h1a != h2
