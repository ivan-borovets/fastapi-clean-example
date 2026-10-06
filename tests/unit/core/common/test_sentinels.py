from app.core.common.sentinels import OMITTED, apply_when_present


def test_passes_omitted_through() -> None:
    sut = apply_when_present

    result = sut(str.upper, OMITTED)

    assert result is OMITTED


def test_passes_none_through() -> None:
    sut = apply_when_present

    result = sut(str.upper, None)

    assert result is None


def test_applies_func_when_value_is_present() -> None:
    sut = apply_when_present

    result = sut(str.upper, "value")

    assert result == "VALUE"
