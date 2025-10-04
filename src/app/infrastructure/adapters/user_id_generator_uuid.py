import uuid6

from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.value_objects.user_id import UserId


class UuidUserIdGenerator(UserIdGenerator):
    def generate(self) -> UserId:
        return UserId(uuid6.uuid7())
