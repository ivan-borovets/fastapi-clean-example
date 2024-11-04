"""
Ensures imperative SQLAlchemy mappings are initialized at application startup.

### Purpose:
In Clean Architecture, domain entities remain agnostic of database
mappings. To integrate with SQLAlchemy, mappings must be explicitly
triggered to link ORM attributes to domain classes. Without this setup,
attempts to interact with unmapped entities in database operations
will lead to runtime errors.

### Solution:
This module imports mapping configurations, enabling ORM registration
without altering domain code or introducing infrastructure concerns.

### Usage:
Import this module in the application factory to initialize mappings at
startup. Additionally, it is beneficial to import this module in
`env.py` for Alembic migrations to ensure all models are available
during database migrations.
"""

# pylint: disable=C0301 (line-too-long)
__all__ = ("session", "user")

from app.infrastructure.user.persistence_sqla import session, user
