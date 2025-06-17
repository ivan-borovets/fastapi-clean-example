from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExceptionSchema:
    description: str


@dataclass(frozen=True, slots=True)
class ExceptionSchemaDetailed(ExceptionSchema):
    details: list[dict[str, Any]] | None = None
