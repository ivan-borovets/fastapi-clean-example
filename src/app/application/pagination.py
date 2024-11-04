from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class PaginationRequest:
    limit: int
    offset: int
