from uuid import UUID

from uuid_utils import compat as uuid_utils

from app.core.common.entities.types_ import UserId


def create_user_id(value: UUID | None = None) -> UserId:
    return UserId(value if value is not None else uuid_utils.uuid7())
