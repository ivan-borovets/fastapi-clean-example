from functools import partial

import pytest

from app.outbound.adapters.bcrypt_password_hasher import BcryptPasswordHasher
from tests.unit.core.common.value_objects.factories import create_raw_password


@pytest.mark.slow
async def test_verifies_correct_password(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    sut = bcrypt_password_hasher()
    password = create_raw_password()
    password_hash = await sut.hash(password)

    is_verified = await sut.verify(raw_password=password, hashed_password=password_hash)

    assert is_verified is True


@pytest.mark.slow
async def test_does_not_verify_incorrect_password(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    sut = bcrypt_password_hasher()
    password = create_raw_password()
    wrong_password = create_raw_password()
    password_hash = await sut.hash(password)

    is_verified = await sut.verify(raw_password=wrong_password, hashed_password=password_hash)

    assert is_verified is False


@pytest.mark.slow
async def test_supports_passwords_longer_than_bcrypt_limit(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    bcrypt_limit = 72
    sut = bcrypt_password_hasher()
    password = create_raw_password("x" * (bcrypt_limit + 1))
    password_hash = await sut.hash(password)

    is_verified = await sut.verify(raw_password=password, hashed_password=password_hash)

    assert is_verified is True


@pytest.mark.slow
async def test_hashes_are_unique_for_same_password(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    sut = bcrypt_password_hasher()
    password = create_raw_password()

    password_hash_1 = await sut.hash(password)
    password_hash_2 = await sut.hash(password)

    assert password_hash_1 != password_hash_2


@pytest.mark.slow
async def test_different_peppers_fail_verification(
    bcrypt_password_hasher: partial[BcryptPasswordHasher],
) -> None:
    password = create_raw_password()
    hasher_1 = bcrypt_password_hasher(pepper=b"PepperA")
    hasher_2 = bcrypt_password_hasher(pepper=b"PepperB")
    password_hash = await hasher_1.hash(password)

    is_verified_1 = await hasher_1.verify(raw_password=password, hashed_password=password_hash)
    is_verified_2 = await hasher_2.verify(raw_password=password, hashed_password=password_hash)

    assert is_verified_1 is True
    assert is_verified_2 is False
