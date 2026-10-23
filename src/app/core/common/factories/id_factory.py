from uuid_utils import compat as uuid_utils

from app.core.common.entities.types_ import UserId


def create_user_id() -> UserId:
    return UserId(uuid_utils.uuid7())
