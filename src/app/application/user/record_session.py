from dataclasses import dataclass
from datetime import datetime

from app.domain.user.vo_user import UserId


@dataclass(eq=False, kw_only=True)
class SessionRecord:
    """
    This class and the classes working with it can be separated into
    a bounded context, enabling a monolithic architecture to become modular.
    """

    id_: str
    user_id: UserId
    expiration: datetime
