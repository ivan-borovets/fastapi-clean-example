from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from app.domain.entities.base.value_object import ValueObject
from app.domain.exceptions.base import DomainError

T = TypeVar("T", bound=ValueObject)


@dataclass(eq=False)
class Entity(ABC, Generic[T]):
    """
    Base class for domain entities, defined by a unique identity (`id`).
    - `id`: Identity that remains constant throughout the entity's lifecycle.
    - Entities are mutable, but are compared solely by their `id`.
    - Subclasses must set `eq=False` to inherit the equality behavior.
    - Add `kw_only=True` in subclasses to enforce named arguments for clarity & safety.
    """

    id_: T

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Prevents modifying the `id` after it's set.
        Other attributes can be changed as usual.
        """
        if name == "id_" and getattr(self, "id_", None) is not None:
            raise DomainError("Changing entity id is not permitted.")
        super().__setattr__(name, value)

    def __eq__(self, other: Any) -> bool:
        """
        Two entities are considered equal if they have the same `id`,
        regardless of other attribute values.
        """
        return isinstance(other, type(self)) and other.id_ == self.id_

    def __hash__(self) -> int:
        """
        Generate a hash based on the immutable `id`.
        This allows entities to be used in hash-based collections.
        """
        return hash(self.id_)
