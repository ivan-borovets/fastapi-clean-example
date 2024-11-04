from dataclasses import dataclass

import pytest

from app.base.a_domain.exceptions import DomainValidationError
from app.base.a_domain.value_object import ValueObject


def test_empty_value_object_raises_error():
    with pytest.raises(DomainValidationError) as exc_info:
        @dataclass(frozen=True, repr=False)
        class EmptyValueObject(ValueObject):
            pass

        EmptyValueObject()

    assert str(exc_info.value) == "EmptyValueObject must have at least one field!"


def test_single_field_repr(single_field_value_object):
    assert repr(single_field_value_object) == "SingleFieldValueObject(123)"


def test_multi_field_repr(multi_field_value_object):
    assert (
        repr(multi_field_value_object)
        == "MultiFieldValueObject(value1=123, value2='abc')"
    )


def test_get_fields_single_field(single_field_value_object):
    assert single_field_value_object.get_fields() == {"value": 123}


def test_get_fields_multi_field(multi_field_value_object):
    assert multi_field_value_object.get_fields() == {"value1": 123, "value2": "abc"}
