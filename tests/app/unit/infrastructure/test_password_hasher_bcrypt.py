from functools import partial

import pytest

from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)
from tests.app.unit.factories.value_objects import create_raw_password


@pytest.mark.slow
@pytest.mark.asyncio
async def test_verifies_correct_password(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    sut = bcrypt_password_hasher()
    pwd = create_raw_password()

    hashed = await sut.hash(pwd)

    assert await sut.verify(raw_password=pwd, hashed_password=hashed)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_does_not_verify_incorrect_password(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    sut = bcrypt_password_hasher()
    correct_pwd = create_raw_password("secure")
    incorrect_pwd = create_raw_password("bruteforce")

    hashed = await sut.hash(correct_pwd)

    assert not await sut.verify(raw_password=incorrect_pwd, hashed_password=hashed)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_supports_passwords_longer_than_bcrypt_limit(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    bcrypt_limit = 72
    sut = bcrypt_password_hasher()
    pwd = create_raw_password("x" * (bcrypt_limit + 1))

    hashed = await sut.hash(pwd)

    assert await sut.verify(raw_password=pwd, hashed_password=hashed)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_hashes_are_unique_for_same_password(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    sut = bcrypt_password_hasher()
    pwd = create_raw_password()

    assert await sut.hash(pwd) != await sut.hash(pwd)


@pytest.mark.slow
@pytest.mark.asyncio
async def test_different_peppers_fail_verification(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    pwd = create_raw_password()
    hasher1 = bcrypt_password_hasher(pepper=b"PepperA")
    hasher2 = bcrypt_password_hasher(pepper=b"PepperB")

    hashed = await hasher1.hash(pwd)

    assert await hasher1.verify(raw_password=pwd, hashed_password=hashed)
    assert not await hasher2.verify(raw_password=pwd, hashed_password=hashed)
