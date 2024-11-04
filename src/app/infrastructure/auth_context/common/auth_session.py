from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.user.value_objects import UserId


@dataclass(eq=False, kw_only=True)
class AuthSession:
    """
    This class can become a domain entity in a new bounded context, enabling
    a monolithic architecture to become modular, while the other classes working
    with it are likely to become application and infrastructure layer components.

    For example, `SignUpHandler` can become an interactor.
    """

    id_: str
    user_id: UserId
    expiration: datetime
