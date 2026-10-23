from dataclasses import dataclass
from typing import ClassVar

from app.core.queries.query_support.exceptions import PaginationError


@dataclass(frozen=True, slots=True, kw_only=True)
class OffsetPaginationParams:
    MIN_LIMIT: ClassVar[int] = 1
    MIN_OFFSET: ClassVar[int] = 0
    MAX_INT32: ClassVar[int] = 2**31 - 1

    limit: int
    offset: int

    def __post_init__(self) -> None:
        self._validate(limit=self.limit, offset=self.offset)

    @classmethod
    def _validate(cls, limit: int, offset: int) -> None:
        if limit < cls.MIN_LIMIT:
            raise PaginationError(f"Limit must be at least {cls.MIN_LIMIT}")
        if limit > cls.MAX_INT32:
            raise PaginationError(f"Limit must be at most {cls.MAX_INT32}")
        if offset < cls.MIN_OFFSET:
            raise PaginationError(f"Offset must be at least {cls.MIN_OFFSET}")
        if offset > cls.MAX_INT32:
            raise PaginationError(f"Offset must be at most {cls.MAX_INT32}")
