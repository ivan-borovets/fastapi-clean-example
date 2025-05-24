from dataclasses import dataclass

import pytest

from app.domain.entities.base import Entity
from app.domain.exceptions.base import DomainError
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class SingleFieldValueObject(ValueObject):
    value: int


@dataclass(eq=False, slots=True)
class SampleEntity(Entity[SingleFieldValueObject]):
    name: str


def test_setattr():
    entity = SampleEntity(id_=SingleFieldValueObject(value=123), name="abc")
    with pytest.raises(DomainError):
        entity.id_ = SingleFieldValueObject(value=456)


def test_eq_hash():
    entity_1 = SampleEntity(id_=SingleFieldValueObject(value=123), name="abc")
    entity_2 = SampleEntity(id_=SingleFieldValueObject(value=123), name="def")
    assert entity_1 == entity_2
    assert hash(entity_1) == hash(entity_2)

    entity_3 = SampleEntity(id_=SingleFieldValueObject(value=456), name="abc")
    assert entity_1 != entity_3
    assert hash(entity_1) != hash(entity_3)
