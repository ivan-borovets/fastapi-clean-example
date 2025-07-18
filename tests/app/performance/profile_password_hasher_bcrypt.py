from line_profiler import LineProfiler

from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
    PasswordPepper,
)


def profile_password_hashing(hasher: BcryptPasswordHasher) -> None:
    raw_password = RawPassword("raw_password")
    hashed = hasher.hash(raw_password)
    hasher.verify(raw_password=raw_password, hashed_password=hashed)


def main() -> None:
    pepper = PasswordPepper("Cayenne!")
    hasher = BcryptPasswordHasher(pepper)

    profiler = LineProfiler()
    profiler.add_function(profile_password_hashing)

    profiler.runcall(profile_password_hashing, hasher)
    profiler.print_stats()


if __name__ == "__main__":
    main()
