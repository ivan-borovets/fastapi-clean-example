from dataclasses import Field, dataclass, fields
from functools import cached_property
from typing import Any, ClassVar, Final, get_args, get_origin

from app.domain.exceptions.base import DomainFieldError


@dataclass(frozen=True, repr=False)
class ValueObject:
    """
    Base class for immutable value objects (VO) in domain.
    Defined by its attributes, which must themselves be immutable.
    For simple cases where only type distinction is required,
    consider using `typing.NewType` instead of subclassing this class.
    """

    def __post_init__(self) -> None:
        """
        :raises DomainFieldError:

        Hook for additional initialization and ensuring invariants.
        Subclasses can override this method to implement custom logic, while
        still calling `super().__post_init__()` to preserve base checks.
        """
        self.__forbid_base_class_instantiation()
        self.__check_field_existence()

    def __forbid_base_class_instantiation(self) -> None:
        """:raises DomainFieldError:"""
        if type(self) is ValueObject:
            raise DomainFieldError("Base ValueObject cannot be instantiated directly.")

    def __check_field_existence(self) -> None:
        """:raises DomainFieldError:"""
        if not self.__instance_fields:
            raise DomainFieldError(
                f"{type(self).__name__} must have at least one field!",
            )

    @cached_property
    def __instance_fields(self) -> tuple[Field[Any], ...]:
        """
        Return only instance fields, exclude `Final[ClassVar[T]]`.

        Since Python 3.13 `Final[ClassVar[T]]` is valid for class constants.
        By typing rules `Final` must wrap `ClassVar`. However, dataclass
        implementation erroneously reports such class variables via
        `fields()`, unlike plain `ClassVar`. We drop them to avoid treating
        class constants as instance attributes.
        """
        instance_fields: list[Field[Any]] = []
        for f in fields(self):
            tp = f.type
            if get_origin(tp) is Final and get_origin(get_args(tp)[0]) is ClassVar:
                continue
            instance_fields.append(f)
        return tuple(instance_fields)

    def __repr__(self) -> str:
        """
        Return string representation of value object.
        - With 1 field: outputs the value only.
        - With 2+ fields: outputs in `name=value` format.
        Subclasses must set `repr=False` for this to take effect.
        """
        return f"{type(self).__name__}({self.__repr_value()})"

    def __repr_value(self) -> str:
        """
        Build string representation of value object.
        - If one field, returns its value.
        - Otherwise, returns comma-separated list of `name=value` pairs.
        """
        items = self.__instance_fields
        if len(items) == 1:
            return f"{getattr(self, items[0].name)!r}"
        return ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in items)
