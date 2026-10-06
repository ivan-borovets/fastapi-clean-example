from pydantic.experimental.missing_sentinel import MISSING

from app.core.common.sentinels import OMITTED
from app.inbound.missing import omit_if_missing


def test_translates_missing_into_omitted() -> None:
    sut = omit_if_missing

    result = sut(MISSING)

    assert result is OMITTED


def test_does_not_translate_none_into_omitted() -> None:
    sut = omit_if_missing

    result = sut(None)

    assert result is None
