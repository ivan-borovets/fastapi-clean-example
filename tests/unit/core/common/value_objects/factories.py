import uuid
from datetime import UTC, datetime

from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime
from tests.unit.core.common.value_objects.types_ import SingleFieldVO


def create_single_field_vo(value: int = 1) -> SingleFieldVO:
    return SingleFieldVO(value)


def create_username(value: str | None = None) -> Username:
    default = f"user_{uuid.uuid4().hex[:8]}"
    return Username(value if value is not None else default)


def create_raw_password(value: str | None = None) -> RawPassword:
    default = uuid.uuid4().hex
    return RawPassword(value if value is not None else default)


def create_utc_datetime(value: datetime | None = None) -> UtcDatetime:
    default = datetime.now(UTC)
    return UtcDatetime(value if value is not None else default)
