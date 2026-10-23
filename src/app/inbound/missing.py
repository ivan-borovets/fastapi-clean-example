from pydantic.experimental.missing_sentinel import MISSING

from app.core.common.sentinels import OMITTED, Omitted


def omit_if_missing[T](value: T) -> T | Omitted:
    return OMITTED if value is MISSING else value
