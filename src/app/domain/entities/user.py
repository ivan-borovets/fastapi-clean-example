"""
- Flat (non-nested) models are best kept anemic (without methods).
  The behavior of such models is described in the domain service.

- When working with non-flat models, such as aggregates, it makes sense
  to have rich models (with methods). The behavior of these models is
  described within the models themselves.
"""

from dataclasses import dataclass

from app.domain.entities.base import Entity
from app.domain.enums.user_role import UserRole
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username.username import Username


@dataclass(eq=False, kw_only=True)
class User(Entity[UserId]):
    username: Username
    password_hash: UserPasswordHash
    role: UserRole
    is_active: bool
