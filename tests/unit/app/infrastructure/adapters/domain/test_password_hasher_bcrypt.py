from app.domain.entities.user.value_objects import RawPassword
from app.infrastructure.adapters.domain.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from app.infrastructure.new_types import PasswordPepper


def test_bcrypt_password_hasher_hash(
    bcrypt_password_hasher: BcryptPasswordHasher,
) -> None:
    test_password: RawPassword = RawPassword("test_password")

    peppered1: bytes = bcrypt_password_hasher._add_pepper(
        test_password,
        bcrypt_password_hasher._pepper,
    )
    peppered2: bytes = bcrypt_password_hasher._add_pepper(
        test_password,
        bcrypt_password_hasher._pepper,
    )

    assert isinstance(peppered1, bytes)
    assert len(peppered1) == 44  # Base64 encoded SHA256 is always 44 bytes
    assert peppered1 == peppered2

    hash1: bytes = bcrypt_password_hasher.hash(test_password)
    hash2: bytes = bcrypt_password_hasher.hash(test_password)

    assert isinstance(hash1, bytes)
    assert hash1.startswith(b"$2b$")  # bcrypt hash prefix
    assert hash1 != hash2  # hashes should be unique due to different salts


def test_bcrypt_password_hasher_verify(
    bcrypt_password_hasher: BcryptPasswordHasher,
) -> None:
    correct_password: RawPassword = RawPassword("test_password")
    wrong_password: RawPassword = RawPassword("wrong_password")

    hashed: bytes = bcrypt_password_hasher.hash(correct_password)

    assert bcrypt_password_hasher.verify(
        raw_password=correct_password,
        hashed_password=hashed,
    )

    assert not bcrypt_password_hasher.verify(
        raw_password=wrong_password,
        hashed_password=hashed,
    )


def test_bcrypt_password_hasher_with_long_password(
    bcrypt_password_hasher: BcryptPasswordHasher,
) -> None:
    long_password: RawPassword = RawPassword(
        "a" * 100
    )  # Exceeds bcrypt's 72-char limit

    hashed: bytes = bcrypt_password_hasher.hash(long_password)

    assert bcrypt_password_hasher.verify(
        raw_password=long_password,
        hashed_password=hashed,
    )


def test_bcrypt_password_hasher_with_special_characters(
    bcrypt_password_hasher: BcryptPasswordHasher,
) -> None:
    special_password: RawPassword = RawPassword("!@#$%^&*()_+{}|:<>?~`-=[]\\;',./№")
    hashed: bytes = bcrypt_password_hasher.hash(special_password)

    assert bcrypt_password_hasher.verify(
        raw_password=special_password,
        hashed_password=hashed,
    )


def test_bcrypt_password_hasher_with_different_pepper() -> None:
    hasher1: BcryptPasswordHasher = BcryptPasswordHasher(PasswordPepper("Pepper1"))
    hasher2: BcryptPasswordHasher = BcryptPasswordHasher(PasswordPepper("Pepper2"))
    password: RawPassword = RawPassword("test_password")

    hashed: bytes = hasher1.hash(password)

    assert hasher1.verify(
        raw_password=password,
        hashed_password=hashed,
    )

    assert not hasher2.verify(
        raw_password=password,
        hashed_password=hashed,
    )
