from collections.abc import Hashable
from typing import Any, Self, cast


class Entity[T: Hashable]:
    """
    Base class for domain entities, defined by a unique identity (`id`).
    Subclassing is optional; any implementation honoring this contract is valid.
    - `id`: Identity that remains constant throughout the entity's lifecycle.
    - Entities are mutable, but are compared solely by their `id`.
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is Entity:
            raise TypeError("Base Entity cannot be instantiated directly.")
        return object.__new__(cls)

    def __init__(self, *, id_: T) -> None:
        self.id_ = id_

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Prevents modifying the `id` after it's set.
        Other attributes can be changed as usual.
        """
        if name == "id_" and getattr(self, "id_", None) is not None:
            raise AttributeError("Changing entity ID is not permitted.")
        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        """
        Two entities are considered equal if they have the same `id`,
        regardless of other attribute values.
        """
        return type(self) is type(other) and cast(Self, other).id_ == self.id_

    def __hash__(self) -> int:
        """
        Generate a hash based on entity type and the immutable `id`.
        This allows entities to be used in hash-based collections and
        reduces the risk of hash collisions between different entity types.
        """
        return hash((type(self), self.id_))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id_={self.id_!r})"
