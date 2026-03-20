from dataclasses import dataclass

from app.core.common.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class SingleFieldVO(ValueObject):
    value: int
