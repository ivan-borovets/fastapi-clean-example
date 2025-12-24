from dataclasses import dataclass

from app.application.common.exceptions.query import PaginationError


@dataclass(frozen=True, slots=True, kw_only=True)
class OffsetPaginationParams:
    """
    raises PaginationError
    """

    limit: int
    offset: int

    def __post_init__(self) -> None:
        """:raises PaginationError:"""
        if self.limit <= 0:
            raise PaginationError(f"Limit must be greater than 0, got {self.limit}")
        if self.offset < 0:
            raise PaginationError(f"Offset must be non-negative, got {self.offset}")
