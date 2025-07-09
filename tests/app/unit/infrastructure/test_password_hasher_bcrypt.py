import pytest

from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
    PasswordPepper,
)
from tests.app.unit.factories.value_objects import create_raw_password


def create_bcrypt_password_hasher(pepper: str = "Habanero!") -> BcryptPasswordHasher:
    return BcryptPasswordHasher(PasswordPepper(pepper))


@pytest.mark.slow
def test_verifies_correct_password() -> None:
    sut = create_bcrypt_password_hasher()
    pwd = create_raw_password()

    hashed = sut.hash(pwd)

    assert sut.verify(raw_password=pwd, hashed_password=hashed)


@pytest.mark.slow
def test_does_not_verify_incorrect_password() -> None:
    sut = create_bcrypt_password_hasher()
    correct_pwd = create_raw_password("secure")
    incorrect_pwd = create_raw_password("bruteforce")

    hashed = sut.hash(correct_pwd)

    assert not sut.verify(raw_password=incorrect_pwd, hashed_password=hashed)


@pytest.mark.slow
def test_supports_passwords_longer_than_bcrypt_limit() -> None:
    bcrypt_limit = 72
    sut = create_bcrypt_password_hasher()
    pwd = create_raw_password("x" * (bcrypt_limit + 1))

    hashed = sut.hash(pwd)

    assert sut.verify(raw_password=pwd, hashed_password=hashed)


@pytest.mark.slow
def test_hashes_are_unique_for_same_password() -> None:
    sut = create_bcrypt_password_hasher()
    pwd = create_raw_password()

    assert sut.hash(pwd) != sut.hash(pwd)


@pytest.mark.slow
def test_different_peppers_fail_verification() -> None:
    pwd = create_raw_password()
    hasher1 = create_bcrypt_password_hasher("PepperA")
    hasher2 = create_bcrypt_password_hasher("PepperB")

    hashed = hasher1.hash(pwd)

    assert hasher1.verify(raw_password=pwd, hashed_password=hashed)
    assert not hasher2.verify(raw_password=pwd, hashed_password=hashed)
