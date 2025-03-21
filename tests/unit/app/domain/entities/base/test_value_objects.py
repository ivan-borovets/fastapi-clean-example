from dataclasses import dataclass

import pytest

from app.domain.entities.base.value_object import ValueObject
from app.domain.exceptions.base import DomainFieldError


@dataclass(frozen=True, slots=True, repr=False)
class SingleFieldValueObject(ValueObject):
    value: int


@dataclass(frozen=True, slots=True, repr=False)
class MultiFieldValueObject(ValueObject):
    value1: int
    value2: str


def test_post_init():
    with pytest.raises(DomainFieldError):
        ValueObject()


def test_repr():
    vo_1 = SingleFieldValueObject(value=123)
    assert repr(vo_1) == "SingleFieldValueObject(123)"
    vo_2 = MultiFieldValueObject(value1=123, value2="abc")
    assert repr(vo_2) == "MultiFieldValueObject(value1=123, value2='abc')"


def test_get_fields():
    vo = MultiFieldValueObject(value1=123, value2="abc")
    assert vo.get_fields() == {"value1": 123, "value2": "abc"}
