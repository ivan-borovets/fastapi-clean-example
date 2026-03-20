from tests.unit.core.common.entities.types_ import (
    NamedEntity,
    NamedEntityId,
    NamedEntitySubclass,
    TaggedEntity,
    TaggedEntityId,
)
from tests.unit.core.common.value_objects.types_ import SingleFieldVO


def create_single_field_vo(value: int = 1) -> SingleFieldVO:
    return SingleFieldVO(value)


def create_named_entity_id(id_: int = 42) -> NamedEntityId:
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


def create_tagged_entity_id(id_: int = 54) -> TaggedEntityId:
    return TaggedEntityId(id_)


def create_tagged_entity(
    id_: int = 54,
    tag: str = "tag",
) -> TaggedEntity:
    return TaggedEntity(id_=TaggedEntityId(id_), tag=tag)
