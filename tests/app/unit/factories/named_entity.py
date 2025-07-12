from dataclasses import dataclass

from app.domain.entities.base import Entity
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class NamedEntityId(ValueObject):
    value: int


@dataclass(eq=False)
class NamedEntity(Entity[NamedEntityId]):
    name: str


@dataclass(eq=False)
class NamedEntitySubclass(NamedEntity):
    value: int


def create_named_entity_id(
    id_: int = 42,
) -> NamedEntityId:
    return NamedEntityId(id_)


def create_named_entity(
    id_: int = 42,
    name: str = "name",
) -> NamedEntity:
    return NamedEntity(NamedEntityId(id_), name)


def create_named_entity_subclass(
    id_: int = 42,
    name: str = "name",
    value: int = 314,
) -> NamedEntitySubclass:
    return NamedEntitySubclass(NamedEntityId(id_), name, value)
