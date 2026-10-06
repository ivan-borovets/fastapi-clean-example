"""
Constraint names shared by mappings and `SqlaFlusher`.

Declare a name here once, reference it from the mapping and from `CONSTRAINT_TO_ERROR`,
repeat its value as a literal in the revision.
"""

from typing import Final

UQ_USERS_USERNAME: Final[str] = "uq_users_username"
