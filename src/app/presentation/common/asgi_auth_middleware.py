import logging
from http.cookies import SimpleCookie
from typing import Any, Literal

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

log = logging.getLogger(__name__)


class ASGIAuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)

        async def modify_cookies(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                self._set_access_token_cookie(request, headers)
                self._delete_access_token_cookie(request, headers)
            await send(message)

        return await self.app(scope, receive, modify_cookies)

    def _set_access_token_cookie(
        self,
        request: Request,
        headers: MutableHeaders,
    ) -> None:
        state = request.state
        new_access_token = getattr(state, "new_access_token", None)
        if new_access_token is None:
            return

        cookie_params: dict[str, Any] = getattr(request.state, "cookie_params", {})
        is_cookie_secure: bool = cookie_params.get("secure", False)
        cookie_samesite: Literal["strict"] | None = cookie_params.get("samesite")

        cookie_header = self._make_cookie_header(
            value=new_access_token,
            is_secure=is_cookie_secure,
            samesite=cookie_samesite,
        )
        headers.append("Set-Cookie", cookie_header)
        log.debug("Cookie with access token '%s' was set.", new_access_token)

    def _delete_access_token_cookie(
        self,
        request: Request,
        headers: MutableHeaders,
    ) -> None:
        is_delete_token: bool = getattr(request.state, "delete_access_token", False)
        if not is_delete_token:
            return

        current_access_token: str | None = request.cookies.get("access_token", None)
        log.debug(
            "Deleting cookie with access token '%s'.",
            current_access_token if current_access_token else "already deleted",
        )

        cookie_header = self._make_cookie_header(value="", max_age=0)
        headers.append("Set-Cookie", cookie_header)
        log.debug("Cookie was deleted.")

    def _make_cookie_header(
        self,
        *,
        value: str,
        is_secure: bool = False,
        samesite: Literal["strict"] | None = None,
        max_age: int | None = None,
    ) -> str:
        cookie = SimpleCookie()
        cookie["access_token"] = value
        cookie["access_token"]["path"] = "/"
        cookie["access_token"]["httponly"] = True

        if is_secure:
            cookie["access_token"]["secure"] = True
        if samesite:
            cookie["access_token"]["samesite"] = samesite
        if max_age is not None:
            cookie["access_token"]["max-age"] = max_age

        return cookie.output(header="").strip()
