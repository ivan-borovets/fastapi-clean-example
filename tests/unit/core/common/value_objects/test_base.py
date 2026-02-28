from dataclasses import FrozenInstanceError, dataclass, field, fields
from typing import ClassVar

import pytest

from app.core.common.value_objects.base import ValueObject
from tests.unit.core.common.value_objects.types_ import SingleFieldVO


@dataclass(frozen=True, slots=True, repr=False)
class MultiFieldVO(ValueObject):
    value1: int
    value2: str


def test_cannot_init() -> None:
    with pytest.raises(TypeError):
        ValueObject()


def test_child_cannot_init_with_no_instance_fields() -> None:
    @dataclass(frozen=True)
    class EmptyVO(ValueObject):
        pass

    with pytest.raises(TypeError):
        EmptyVO()


def test_child_cannot_init_with_only_class_fields() -> None:
    @dataclass(frozen=True)
    class ClassFieldsVO(ValueObject):
        foo: ClassVar[int] = 0
        bar: ClassVar[str] = "baz"

    with pytest.raises(TypeError):
        ClassFieldsVO()


def test_class_field_not_in_dataclass_fields() -> None:
    @dataclass(frozen=True)
    class MixedFieldsVO(ValueObject):
        foo: ClassVar[int] = 0
        bar: str

    sut = MixedFieldsVO(bar="baz")

    sut_fields = fields(sut)
    assert len(sut_fields) == 1
    assert sut_fields[0].name == "bar"
    assert sut_fields[0].type is str
    assert getattr(sut, sut_fields[0].name) == "baz"


def test_class_field_not_broken_by_slots() -> None:
    @dataclass(frozen=True, slots=True)
    class MixedFieldsVO(ValueObject):
        foo: ClassVar[int] = 0
        bar: str

    assert MixedFieldsVO.foo == 0


def test_class_field_final_equivalence() -> None:
    @dataclass(frozen=True)
    class MixedFieldsVO:
        a: ClassVar[int] = 1
        b: ClassVar[str] = "bar"
        c: str = "baz"

    sut_field_names = [f.name for f in fields(MixedFieldsVO)]

    assert sut_field_names == ["c"]


def test_is_immutable() -> None:
    sut = SingleFieldVO(1)

    with pytest.raises(FrozenInstanceError):
        # noinspection PyDataclass
        sut.value = sut.value + 1  # type: ignore[misc]


def test_equality() -> None:
    vo_value_1 = 1
    vo_value_2 = "Alice"
    sut1 = MultiFieldVO(value1=vo_value_1, value2=vo_value_2)
    sut2 = MultiFieldVO(value1=vo_value_1, value2=vo_value_2)

    assert sut1 == sut2


def test_inequality() -> None:
    vo_value_1 = 1
    sut1 = MultiFieldVO(value1=vo_value_1, value2="Alice")
    sut2 = MultiFieldVO(value1=vo_value_1, value2="Bob")

    assert sut1 != sut2


def test_single_field_vo_repr() -> None:
    sut = SingleFieldVO(1)

    assert repr(sut) == "SingleFieldVO(1)"


def test_multi_field_vo_repr() -> None:
    sut = MultiFieldVO(value1=1, value2="Alice")

    assert repr(sut) == "MultiFieldVO(value1=1, value2='Alice')"


def test_class_field_not_in_repr() -> None:
    @dataclass(frozen=True, repr=False)
    class MixedFieldsVO(ValueObject):
        baz: int
        foo: ClassVar[int] = 0
        bar: ClassVar[str] = "baz"

    sut = MixedFieldsVO(baz=1)

    assert repr(sut) == "MixedFieldsVO(1)"


def test_hidden_field_not_in_repr() -> None:
    @dataclass(frozen=True, repr=False)
    class HiddenFieldVO(ValueObject):
        visible: int
        hidden: int = field(repr=False)

    sut = HiddenFieldVO(1, 2)

    assert repr(sut) == "HiddenFieldVO(1)"


def test_all_fields_hidden_repr() -> None:
    @dataclass(frozen=True, repr=False)
    class HiddenFieldVO(ValueObject):
        hidden_1: int = field(repr=False)
        hidden_2: int = field(repr=False)

    sut = HiddenFieldVO(1, 2)

    assert repr(sut) == "HiddenFieldVO(<hidden>)"


def test_is_hashable() -> None:
    sut1 = MultiFieldVO(value1=123, value2="abc")
    sut2 = MultiFieldVO(value1=123, value2="abc")
    sut3 = MultiFieldVO(value1=456, value2="def")

    dict_with_sut_as_keys = {
        sut1: "value1",
        sut3: "value3",
    }

    assert dict_with_sut_as_keys[sut1] == "value1"
    assert dict_with_sut_as_keys[sut2] == "value1"
    assert dict_with_sut_as_keys[sut3] == "value3"
    assert len(dict_with_sut_as_keys) == 2
    assert hash(sut1) == hash(sut2) != hash(sut3)
