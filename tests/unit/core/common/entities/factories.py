from tests.unit.core.common.entities.types_ import (
    NamedEntity,
    NamedEntityId,
    NamedEntitySubclass,
    TaggedEntity,
    TaggedEntityId,
)


def create_named_entity_id(id_: int = 42) -> NamedEntityId:
    return NamedEntityId(id_)


def create_named_entity(
    id_: int = 42,
    name: str = "name",
) -> NamedEntity:
    return NamedEntity(id_=create_named_entity_id(id_), name=name)


def create_named_entity_subclass(
    id_: int = 42,
    name: str = "name",
    value: int = 314,
) -> NamedEntitySubclass:
    return NamedEntitySubclass(id_=create_named_entity_id(id_), name=name, value=value)


def create_tagged_entity_id(id_: int = 54) -> TaggedEntityId:
    return TaggedEntityId(id_)


def create_tagged_entity(id_: int = 54, tag: str = "tag") -> TaggedEntity:
    return TaggedEntity(id_=create_tagged_entity_id(id_), tag=tag)
