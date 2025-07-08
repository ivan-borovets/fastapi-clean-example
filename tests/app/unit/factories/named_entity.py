from dataclasses import dataclass

from app.domain.entities.base import Entity
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class NamedEntityId(ValueObject):
    value: int


@dataclass(eq=False, slots=True)
class NamedEntity(Entity[NamedEntityId]):
    name: str


def create_named_entity_id(
    id_: int = 42,
) -> NamedEntityId:
    return NamedEntityId(id_)


def create_named_entity(
    id_: int = 42,
    name: str = "name",
) -> NamedEntity:
    id_vo = create_named_entity_id(id_)
    return NamedEntity(id_vo, name)
