from dataclasses import dataclass

from app.core.common.entities.base import Entity
from app.core.common.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class NamedEntityId(ValueObject):
    value: int


class NamedEntity(Entity[NamedEntityId]):
    def __init__(self, *, id_: NamedEntityId, name: str) -> None:
        super().__init__(id_=id_)
        self.name = name


class NamedEntitySubclass(NamedEntity):
    def __init__(self, *, id_: NamedEntityId, name: str, value: int) -> None:
        super().__init__(id_=id_, name=name)
        self.value = value


@dataclass(frozen=True, slots=True, repr=False)
class TaggedEntityId(ValueObject):
    value: int


class TaggedEntity(Entity[TaggedEntityId]):
    def __init__(self, *, id_: TaggedEntityId, tag: str) -> None:
        super().__init__(id_=id_)
        self.tag = tag
