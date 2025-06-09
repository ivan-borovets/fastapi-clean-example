from dataclasses import dataclass
from typing import NewType

PostgresDsn = NewType("PostgresDsn", str)


@dataclass(frozen=True, slots=True)
class SqlaEngineConfig:
    echo: bool
    echo_pool: bool
    pool_size: int
    max_overflow: int
