from line_profiler import LineProfiler

from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
    PasswordPepper,
)


def run_operations(hasher: BcryptPasswordHasher) -> None:
    raw_password = RawPassword("raw_password")
    hashed = hasher.hash(raw_password)
    hasher.verify(raw_password=raw_password, hashed_password=hashed)


def create_hasher() -> BcryptPasswordHasher:
    pepper = PasswordPepper("Cayenne!")
    return BcryptPasswordHasher(pepper)


def create_profiler() -> LineProfiler:
    profiler = LineProfiler()
    profiler.add_function(run_operations)
    return profiler


def run_profiling(
    profiler: LineProfiler,
    hasher: BcryptPasswordHasher,
) -> None:
    profiler.runcall(run_operations, hasher)  # type: ignore[no-untyped-call]
    profiler.print_stats()


def main() -> None:
    hasher = create_hasher()
    profiler = create_profiler()
    run_profiling(profiler, hasher)


if __name__ == "__main__":
    main()
