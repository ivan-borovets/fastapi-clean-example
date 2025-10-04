from dataclasses import dataclass, fields

from app.domain.exceptions.base import DomainFieldError


@dataclass(frozen=True, slots=True, repr=False)
class ValueObject:
    """
    Base class for immutable value objects (VO) in domain.
    Defined by instance attributes only; these must be immutable.
    For simple type tagging, consider `typing.NewType` instead of subclassing.

    Repr policy: `__repr__` includes only fields with `repr=True`;
    fields with `repr=False` are omitted to avoid leaking secrets.
    If no fields have `repr=True`, '<hidden>' is shown.

    Typing/runtime mismatch:
    By current typing rules, `Final` should wrap `ClassVar` → `Final[ClassVar[T]]`.
    At runtime, `dataclasses.fields()` includes it as an instance field (and with
    `__slots__` it becomes a `member_descriptor`). Use `ClassVar[Final[T]]`
    (or `ClassVar[T]`) so class constants are not treated as instance attributes.
    As of now, mypy does not enforce `Final` inside `ClassVar`; reassignment is
    allowed, so `ClassVar[Final[T]]` is effectively `ClassVar[T]`. We keep `Final`
    for forward-compatibility, expecting future enforcement.

    References:
    https://github.com/python/cpython/issues/89547
    https://github.com/python/mypy/issues/19607
    """

    def __post_init__(self) -> None:
        """
        :raises DomainFieldError:

        Hook for additional initialization and ensuring invariants.
        Subclasses can override this method to implement custom logic, while
        still calling `super().__post_init__()` to preserve base checks.

        Note on slotted dataclasses:
        With `slots=True`, the dataclass transformation may replace the class
        object; a zero-arg `super()` in a subclass `__post_init__` can then raise
        `TypeError`. In such cases, call the base with two-arg super, e.g.:
            `super(Username, self).__post_init__()`
        (or invoke directly: `ValueObject.__post_init__(self)`).

        Reference: https://github.com/python/cpython/issues/90562
        """
        self.__forbid_base_class_instantiation()
        self.__check_field_existence()

    def __forbid_base_class_instantiation(self) -> None:
        """:raises DomainFieldError:"""
        if type(self) is ValueObject:
            raise DomainFieldError("Base ValueObject cannot be instantiated directly.")

    def __check_field_existence(self) -> None:
        """:raises DomainFieldError:"""
        if not fields(self):
            raise DomainFieldError(
                f"{type(self).__name__} must have at least one field!",
            )

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
