from dataclasses import dataclass
from datetime import datetime

from app.base.a_domain.value_object import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class SessionId(ValueObject):
    value: str


@dataclass(frozen=True, slots=True, repr=False)
class SessionExpiration(ValueObject):
    value: datetime
