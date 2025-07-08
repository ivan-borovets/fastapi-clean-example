from dataclasses import FrozenInstanceError

import pytest

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject
from tests.app.unit.factories.value_objects import (
    create_multi_field_vo,
    create_single_field_vo,
)


def test_is_not_empty() -> None:
    class EmptyValueObject(ValueObject):
        pass

    with pytest.raises(DomainFieldError):
        EmptyValueObject()


def test_is_immutable() -> None:
    vo_value = 123
    sut = create_single_field_vo(vo_value)

    with pytest.raises(FrozenInstanceError):
        # noinspection PyDataclass
        sut.value = vo_value + 1  # type: ignore[misc]


def test_equality() -> None:
    vo1 = create_multi_field_vo()
    vo2 = create_multi_field_vo()

    assert vo1 == vo2


def test_inequality() -> None:
    vo1 = create_multi_field_vo(value2="one")
    vo2 = create_multi_field_vo(value2="two")

    assert vo1 != vo2


def test_single_field_vo_repr() -> None:
    sut = create_single_field_vo(123)

    assert repr(sut) == "SingleFieldVO(123)"


def test_multi_field_vo_repr() -> None:
    sut = create_multi_field_vo(value1=123, value2="abc")

    assert repr(sut) == "MultiFieldVO(value1=123, value2='abc')"


def test_returns_fields_as_dict() -> None:
    sut = create_multi_field_vo(value1=123, value2="abc")

    assert sut.get_fields() == {"value1": 123, "value2": "abc"}
