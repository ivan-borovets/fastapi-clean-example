from dataclasses import dataclass

from app.domain.entities.base import Entity
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TaggedEntityId(ValueObject):
    value: int


@dataclass(eq=False)
class TaggedEntity(Entity[TaggedEntityId]):
    tag: str


def create_tagged_entity_id(
    id_: int = 54,
) -> TaggedEntityId:
    return TaggedEntityId(id_)


def create_tagged_entity(
    id_: int = 54,
    tag: str = "tag",
) -> TaggedEntity:
    return TaggedEntity(TaggedEntityId(id_), tag)
