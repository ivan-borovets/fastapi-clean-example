from dataclasses import dataclass
from enum import StrEnum


class SortingOrder(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass(frozen=True, slots=True, kw_only=True)
class SortingParams:
    field: str
    order: SortingOrder
