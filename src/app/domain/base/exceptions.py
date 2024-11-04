class DomainError(Exception):
    """
    Exception for violations of fundamental domain rules, such as attempts to change
    the immutable `id` of an Entity, as well as for complex business rule violations.

    Not for:
    - Single attribute validation (use `DomainFieldError` instead).
    - Application, infrastructure, or system errors.
    """


class DomainFieldError(DomainError):
    """
    Exception for validation errors in Value Objects and Entity field values.

    Use cases:
    1. Violations of Value Object invariants during creation.
    2. Single-field validation errors in Entities.

    Not for:
    - Complex business rule violations (use `DomainError` instead).
    - Input validation at application boundaries.
    """
