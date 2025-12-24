from dataclasses import dataclass

from app.domain.entities.base import Entity
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class TaggedEntityId(ValueObject):
    value: int


class TaggedEntity(Entity[TaggedEntityId]):
    def __init__(self, *, id_: TaggedEntityId, tag: str) -> None:
        super().__init__(id_=id_)
        self.tag = tag


def create_tagged_entity_id(id_: int = 54) -> TaggedEntityId:
    return TaggedEntityId(id_)


def create_tagged_entity(id_: int = 54, tag: str = "tag") -> TaggedEntity:
    return TaggedEntity(id_=TaggedEntityId(id_), tag=tag)
