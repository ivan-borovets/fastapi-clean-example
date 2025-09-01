"""
- In the early stages of development
  when the domain model is not yet clearly defined,
  it is wiser to keep entities
  flat (non-nested) and anemic (without behavior).
  Their behavior resides in separate domain services,
  even though this weakens encapsulation.

- Once the core logic is well established,
  some entities can, as aggregate roots,
  become non-flat and rich (with behavior).
  This best enforces invariants
  but can be tricky to design once and for all.

- Prefer rich value objects early,
  freeing entities and services
  from an excessive burden of local rules.
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
