import pytest

from app.domain.entities.base import Entity
from tests.app.unit.factories.named_entity import (
    create_named_entity,
    create_named_entity_id,
    create_named_entity_subclass,
)
from tests.app.unit.factories.tagged_entity import create_tagged_entity
from tests.app.unit.factories.value_objects import create_single_field_vo


def test_cannot_init() -> None:
    vo = create_single_field_vo()

    with pytest.raises(TypeError):
        Entity(id_=vo)


@pytest.mark.parametrize(
    "new_id",
    [
        pytest.param(1, id="same_id"),
        pytest.param(999, id="different_id"),
    ],
)
def test_entity_id_cannot_be_changed(new_id: int) -> None:
    sut = create_named_entity(id_=1)

    with pytest.raises(AttributeError):
        sut.id_ = create_named_entity_id(new_id)


def test_entity_is_mutable_except_id() -> None:
    sut = create_named_entity(name="Alice")
    new_name = "Bob"

    sut.name = new_name

    assert sut.name == new_name


@pytest.mark.parametrize(
    ("name1", "name2"),
    [
        pytest.param("Alice", "Alice", id="same_name"),
        pytest.param("Alice", "Bob", id="different_name"),
    ],
)
def test_same_type_entities_with_same_id_are_equal(
    name1: str,
    name2: str,
) -> None:
    e1 = create_named_entity(name=name1)
    e2 = create_named_entity(name=name2)

    assert e1 == e2


def test_same_type_entities_with_different_id_are_not_equal() -> None:
    e1 = create_named_entity(id_=1)
    e2 = create_named_entity(id_=2)

    assert e1 != e2


def test_entities_of_different_types_are_not_equal() -> None:
    sut_id = 1
    e1 = create_named_entity(id_=sut_id)
    e2 = create_tagged_entity(id_=sut_id)

    assert e1 != e2


def test_entity_is_not_equal_to_subclass_with_same_id() -> None:
    parent = create_named_entity()
    child = create_named_entity_subclass(
        id_=parent.id_.value,
        name=parent.name,
        value=1,
    )

    assert parent.__eq__(child) is False
    assert child.__eq__(parent) is False


def test_equal_entities_have_equal_hash() -> None:
    sut_id = 1
    e1 = create_named_entity(id_=sut_id, name="Alice")
    e2 = create_named_entity(id_=sut_id, name="Bob")

    assert e1 == e2
    assert hash(e1) == hash(e2)


def test_entity_can_be_used_in_set() -> None:
    e1 = create_named_entity(id_=1, name="Alice")
    e2 = create_named_entity(id_=1, name="Bob")
    e3 = create_named_entity(id_=2)
    e4 = create_tagged_entity(id_=1)

    entity_set = {e1, e2, e3, e4}

    assert len(entity_set) == 3


def test_entity_repr_shows_id() -> None:
    sut = create_named_entity(id_=1, name="Alice")

    repr_str = repr(sut)

    assert repr_str == "NamedEntity(id_=NamedEntityId(1))"
