from abc import ABC
from dataclasses import asdict, dataclass, fields
from typing import Any

from app.base.a_domain.exceptions import DomainValidationError


@dataclass(frozen=True, repr=False)
class ValueObject(ABC):
    """
    Base class for immutable value objects in the domain.
    - Defined by its attributes, which must also be immutable.
    - Use `slots=True` in subclasses for memory optimization and to prevent dynamic
     attribute creation.
    - Subclasses should set `repr=False` to use the custom `__repr__` implementation
     from this class.
    """

    def __post_init__(self) -> None:
        """
        Hook for additional initialization if needed. Subclasses can override this
        method for custom validation logic, while still calling `super()` to ensure
        base check is done.
        """
        if not fields(self):
            raise DomainValidationError(
                f"{type(self).__name__} must have at least one field!"
            )

    def __repr__(self) -> str:
        """
        Returns a string representation of the value object.
        - With 1 field: outputs the value only.
        - With 2+ fields: outputs in `name=value` format.
        Subclasses must set `repr=False` in @dataclass for this to work.
        """
        return f"{type(self).__name__}({self._repr_value()})"

    def _repr_value(self) -> str:
        """
        Helper to build a string representation of the value object.
        - If there is one field, returns the value of that field.
        - Otherwise, returns a comma-separated list of `name=value` pairs.
        """
        all_fields = fields(self)
        if len(all_fields) == 1:
            return f"{getattr(self, all_fields[0].name)!r}"
        return ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in all_fields)

    def get_fields(self) -> dict[str, Any]:
        """
        Returns a dictionary of all attributes and their values.
        """
        return asdict(self)
