from dataclasses import dataclass, fields
from typing import Any, Self


@dataclass(frozen=True, slots=True, repr=False)
class ValueObject:
    """
    Base class for immutable value objects (VO).
    Subclassing is optional; any implementation honoring this contract is valid.
    Defined by instance attributes only; these must be immutable.
    For simple type tagging, consider `typing.NewType` instead of subclassing.

    Repr policy: `__repr__` includes only fields with `repr=True`;
    fields with `repr=False` are omitted to avoid leaking secrets.
    If no fields have `repr=True`, '<hidden>' is shown.

    Typing/runtime note for class constants:
    Don't combine `ClassVar` with `Final` in any order for safety reasons.
    Python 3.12 doesn't support this at runtime, Python 3.13 has compatibility issues.

    Dataclasses exclude only `ClassVar` attributes from instance fields, so use `ClassVar[T]`
    for class-level constants and enforce non-reassignment via convention/linting/type-checker.
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is ValueObject:
            raise TypeError("Base ValueObject cannot be instantiated directly.")
        if not fields(cls):
            raise TypeError(f"{cls.__name__} must have at least one field!")
        return object.__new__(cls)

    def __post_init__(self) -> None:
        """
        Hook for additional initialization and ensuring invariants.
        If this hook ever becomes non-empty, subclasses must call `super().__post_init__()`.
        """

    def __repr__(self) -> str:
        """
        Return string representation of value object.
        - With 1 field: outputs the value only.
        - With 2+ fields: outputs in `name=value` format.
        Subclasses must set `repr=False` for this to take effect.

        Set `repr=False` on fields you want to hide;
        if all fields are hidden, '<hidden>' is shown.
        """
        return f"{type(self).__name__}({self.__repr_value()})"

    def __repr_value(self) -> str:
        """
        Build string representation of value object.
        - If one field, returns its value.
        - Otherwise, returns comma-separated list of `name=value` pairs.
        """
        items = [f for f in fields(self) if f.repr]
        if not items:
            return "<hidden>"
        if len(items) == 1:
            return f"{getattr(self, items[0].name)!r}"
        return ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in items)
