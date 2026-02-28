from dataclasses import dataclass
from typing import ClassVar

from app.core.queries.query_support.exceptions import PaginationError


@dataclass(frozen=True, slots=True, kw_only=True)
class OffsetPaginationParams:
    MAX_INT32: ClassVar[int] = 2**31 - 1

    limit: int
    offset: int

    def __post_init__(self) -> None:
        self._validate(limit=self.limit, offset=self.offset)

    @classmethod
    def _validate(cls, limit: int, offset: int) -> None:
        if limit <= 0:
            raise PaginationError(f"Limit must be greater than 0, got {limit}")
        if limit > cls.MAX_INT32:
            raise PaginationError(f"Limit cannot be greater than {cls.MAX_INT32}, got {limit}")
        if offset < 0:
            raise PaginationError(f"Offset must be non-negative, got {offset}")
        if offset > cls.MAX_INT32:
            raise PaginationError(f"Offset cannot be greater than {cls.MAX_INT32}, got {offset}")
