from dataclasses import dataclass

from app.domain.entities.base import Entity
from app.domain.value_objects.base import ValueObject


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


def create_named_entity_id(
    id_: int = 42,
) -> NamedEntityId:
    return NamedEntityId(id_)


def create_named_entity(
    id_: int = 42,
    name: str = "name",
) -> NamedEntity:
    return NamedEntity(id_=NamedEntityId(id_), name=name)


def create_named_entity_subclass(
    id_: int = 42,
    name: str = "name",
    value: int = 314,
) -> NamedEntitySubclass:
    return NamedEntitySubclass(id_=NamedEntityId(id_), name=name, value=value)
