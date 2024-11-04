from line_profiler import LineProfiler

from app.common.c_infrastructure.custom_types import PasswordPepper
from app.distinct.user.c_infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)


hasher = BcryptPasswordHasher(PasswordPepper("Cayenne!"))
profile = LineProfiler()
profile.add_function(hasher.hash)
profile.add_function(hasher.verify)


@profile
def main():
    raw_password = "raw_password"
    hashed = hasher.hash(raw_password)
    hasher.verify(raw_password=raw_password, hashed_password=hashed)


if __name__ == "__main__":
    profile.run("main()")
    profile.print_stats()
