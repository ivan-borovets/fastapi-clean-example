from typing import Final, NewType

from starlette.requests import Request

CookieName = NewType("CookieName", str)

STAGED_COOKIE: Final[str] = "staged_cookie"


class CookieManager:
    def __init__(self, request: Request, cookie_name: CookieName) -> None:
        self._request = request
        self._cookie_name = cookie_name

    def read(self) -> str | None:
        return self._request.cookies.get(self._cookie_name)

    def stage_set(self, value: str) -> None:
        setattr(self._request.state, STAGED_COOKIE, value)

    def stage_delete(self) -> None:
        setattr(self._request.state, STAGED_COOKIE, None)
