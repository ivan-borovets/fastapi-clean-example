from typing import Any

from fastapi_error_map import ErrorAwareRouter, ErrorMap, OnError, structured


def make_error_aware_router(
    *,
    error_map: ErrorMap | None = None,
    on_error: OnError | None = None,
    warn_on_unmapped: bool = True,
    **kwargs: Any,
) -> ErrorAwareRouter:
    return ErrorAwareRouter(
        translator_factory=structured(),
        error_map=error_map,
        on_error=on_error,
        warn_on_unmapped=warn_on_unmapped,
        **kwargs,
    )
