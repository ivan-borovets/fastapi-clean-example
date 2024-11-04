import logging
from http.cookies import SimpleCookie
from typing import Any, Literal

from fastapi import FastAPI
from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import Message, Receive, Scope, Send

log = logging.getLogger(__name__)


class ASGIAuthMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request: Request = Request(scope)

        async def modify_cookies(message: Message) -> None:
            if message["type"] != "http.response.start":
                await send(message)
                return

            headers: MutableHeaders = MutableHeaders(scope=message)

            self._set_access_token_cookie(request, headers)
            self._delete_access_token_cookie(request, headers)

            await send(message)

        await self.app(scope, receive, modify_cookies)

    def _set_access_token_cookie(
        self, request: Request, headers: MutableHeaders
    ) -> None:
        new_access_token: str | None = getattr(request.state, "new_access_token", None)
        if new_access_token is None:
            return

        cookie_params: dict[str, Any] = getattr(request.state, "cookie_params", {})

        is_cookie_secure: bool = cookie_params.get("secure", False)
        cookie_samesite: Literal["strict"] | None = cookie_params.get("samesite", None)

        cookie: SimpleCookie = SimpleCookie()
        cookie["access_token"] = new_access_token
        cookie["access_token"]["path"] = "/"
        cookie["access_token"]["httponly"] = True

        if is_cookie_secure:
            cookie["access_token"]["secure"] = True
        if cookie_samesite is not None:
            cookie["access_token"]["samesite"] = cookie_samesite

        headers.append("Set-Cookie", cookie.output(header="").strip())
        log.debug("Cookie with access token '%s' was set.", new_access_token)

    def _delete_access_token_cookie(
        self, request: Request, headers: MutableHeaders
    ) -> None:
        is_delete_token: bool = getattr(request.state, "delete_access_token", False)
        if not is_delete_token:
            return

        current_access_token: str | None = request.cookies.get("access_token", None)
        log.debug(
            "Deleting cookie with access token '%s'.",
            current_access_token if current_access_token else "already deleted",
        )

        cookie: SimpleCookie = SimpleCookie()
        cookie["access_token"] = ""  # nosec
        cookie["access_token"]["path"] = "/"
        cookie["access_token"]["httponly"] = True
        cookie["access_token"]["max-age"] = 0

        headers.append("Set-Cookie", cookie.output(header="").strip())

        log.debug("Cookie was deleted.")
