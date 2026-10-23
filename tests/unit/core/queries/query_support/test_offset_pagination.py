import pytest

from app.core.queries.query_support.exceptions import PaginationError
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams


def test_accepts_valid_params() -> None:
    sut = OffsetPaginationParams(limit=10, offset=0)

    assert sut.limit == 10
    assert sut.offset == 0


def test_limit_must_be_greater_than_0() -> None:
    with pytest.raises(PaginationError):
        OffsetPaginationParams(limit=0, offset=0)


def test_limit_cannot_exceed_max_int32() -> None:
    with pytest.raises(PaginationError):
        OffsetPaginationParams(
            limit=OffsetPaginationParams.MAX_INT32 + 1,
            offset=0,
        )


def test_offset_must_be_non_negative() -> None:
    with pytest.raises(PaginationError):
        OffsetPaginationParams(limit=1, offset=-1)


def test_offset_cannot_exceed_max_int32() -> None:
    with pytest.raises(PaginationError):
        OffsetPaginationParams(
            limit=1,
            offset=OffsetPaginationParams.MAX_INT32 + 1,
        )
