from dataclasses import dataclass
from typing import NewType

from app.core.common.entities.types_ import UserId
from app.core.common.value_objects.utc_datetime import UtcDatetime

SessionId = NewType("SessionId", str)


@dataclass(eq=False, kw_only=True)
class AuthSession:
    """
    This class can become a domain entity in a new bounded context, enabling
    a monolithic architecture to become modular, while the other classes working
    with it are likely to become core and outbound layer components.

    For example, `LogIn` can become an interactor.
    """

    id_: SessionId
    user_id: UserId
    expiration: UtcDatetime
