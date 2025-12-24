from dataclasses import FrozenInstanceError, dataclass, field, fields
from typing import ClassVar, Final

import pytest

from app.domain.value_objects.base import ValueObject
from tests.app.unit.factories.value_objects import (
    create_multi_field_vo,
    create_single_field_vo,
)


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
        bar: ClassVar[Final[str]] = "baz"

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
        b: ClassVar[Final[str]] = "bar"
        c: str = "baz"

    sut_field_names = [f.name for f in fields(MixedFieldsVO)]

    assert sut_field_names == ["c"]


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


def test_class_field_not_in_repr() -> None:
    @dataclass(frozen=True, repr=False)
    class MixedFieldsVO(ValueObject):
        baz: int
        foo: ClassVar[int] = 0
        bar: ClassVar[Final[str]] = "baz"

    sut = MixedFieldsVO(baz=1)

    assert repr(sut) == "MixedFieldsVO(1)"


def test_hidden_field_not_in_repr() -> None:
    @dataclass(frozen=True, repr=False)
    class HiddenFieldVO(ValueObject):
        visible: int
        hidden: int = field(repr=False)

    sut = HiddenFieldVO(123, 456)

    assert repr(sut) == "HiddenFieldVO(123)"


def test_all_fields_hidden_repr() -> None:
    @dataclass(frozen=True, repr=False)
    class HiddenFieldVO(ValueObject):
        hidden_1: int = field(repr=False)
        hidden_2: int = field(repr=False)

    sut = HiddenFieldVO(123, 456)

    assert repr(sut) == "HiddenFieldVO(<hidden>)"
