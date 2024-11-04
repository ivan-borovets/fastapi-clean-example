from app.domain.user.value_objects import RawPassword
from app.infrastructure.new_types import PasswordPepper
from app.infrastructure.adapters.domain.bcrypt_password_hasher import BcryptPasswordHasher


def test_bcrypt_password_hasher_hash(bcrypt_password_hasher):
    hasher = bcrypt_password_hasher

    test_password = "test_password"
    test_password_vo = RawPassword(test_password)

    first_peppered = hasher._add_pepper(test_password_vo, hasher._pepper)
    second_peppered = hasher._add_pepper(test_password_vo, hasher._pepper)

    first_peppered_salted = hasher.hash(test_password_vo)
    second_peppered_salted = hasher.hash(test_password_vo)

    assert isinstance(first_peppered, bytes)
    assert len(first_peppered) == 44  # Base64 encoded SHA256 is always 44 bytes
    assert first_peppered == second_peppered
    assert isinstance(first_peppered_salted, bytes)
    assert first_peppered_salted.startswith(b"$2b$")  # bcrypt hash prefix
    assert first_peppered_salted != second_peppered_salted


def test_bcrypt_password_hasher_verify(bcrypt_password_hasher):
    hasher = bcrypt_password_hasher

    test_password = "test_password"
    test_password_vo = RawPassword(test_password)

    wrong_password = "wrong_password"
    wrong_password_vo = RawPassword(wrong_password)

    hashed = hasher.hash(test_password_vo)

    assert hasher.verify(raw_password=test_password_vo, hashed_password=hashed) is True
    assert hasher.verify(raw_password=wrong_password_vo, hashed_password=hashed) is False


def test_bcrypt_password_hasher_with_long_password(bcrypt_password_hasher):
    hasher = bcrypt_password_hasher

    long_password = "a" * 100  # Password longer than 72 characters
    long_password_vo = RawPassword(long_password)

    hashed = hasher.hash(long_password_vo)

    assert hasher.verify(raw_password=long_password_vo, hashed_password=hashed) is True


def test_bcrypt_password_hasher_with_special_characters(bcrypt_password_hasher):
    hasher = bcrypt_password_hasher

    special_password = "!@#$%^&*()_+{}|:<>?~`-=[]\\;',./№"
    special_password_vo = RawPassword(special_password)

    hashed = hasher.hash(special_password_vo)

    assert hasher.verify(raw_password=special_password_vo, hashed_password=hashed) is True


def test_bcrypt_password_hasher_with_different_pepper():
    hasher1 = BcryptPasswordHasher(PasswordPepper("Pepper1"))
    hasher2 = BcryptPasswordHasher(PasswordPepper("Pepper2"))

    test_password = "test_password"
    test_password_vo = RawPassword(test_password)

    hashed1 = hasher1.hash(test_password_vo)

    assert hasher1.verify(raw_password=test_password_vo, hashed_password=hashed1) is True
    assert hasher2.verify(raw_password=test_password_vo, hashed_password=hashed1) is False
