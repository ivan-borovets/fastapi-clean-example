from unittest.mock import Mock

from line_profiler import LineProfiler

from app.domain.value_objects.raw_password import RawPassword
from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)


def profile_password_hashing(hasher: BcryptPasswordHasher) -> None:
    raw_password = RawPassword("raw_password")
    hashed = hasher.hash_sync(raw_password)
    hasher.verify_sync(raw_password, hashed)


def main() -> None:
    hasher = BcryptPasswordHasher(
        pepper="Cayenne!",
        work_factor=11,
        executor=Mock(),
    )

    profiler = LineProfiler()
    profiler.add_function(profile_password_hashing)

    profiler.runcall(profile_password_hashing, hasher)
    profiler.print_stats()


if __name__ == "__main__":
    main()
