class DomainTypeError(Exception):
    """Invalid construction of domain types (Value Objects)."""


class DomainError(Exception):
    """Domain rule violation not tied to domain type construction."""
