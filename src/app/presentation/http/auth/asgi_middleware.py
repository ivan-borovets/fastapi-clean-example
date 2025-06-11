import logging
from http.cookies import SimpleCookie
from typing import Literal

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.presentation.http.auth.constants import (
    COOKIE_ACCESS_TOKEN_NAME,
    REQUEST_STATE_COOKIE_PARAMS_KEY,
    REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY,
    REQUEST_STATE_NEW_ACCESS_TOKEN_KEY,
)
from app.presentation.http.auth.cookie_params import (
    CookieParams,
)

log = logging.getLogger(__name__)


class ASGIAuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                self._maybe_set_cookie(request, headers)
                self._maybe_delete_cookie(request, headers)
            await send(message)

        return await self.app(scope, receive, send_wrapper)

    def _maybe_set_cookie(self, request: Request, headers: MutableHeaders) -> None:
        new_access_token: str | None = getattr(
            request.state,
            REQUEST_STATE_NEW_ACCESS_TOKEN_KEY,
            None,
        )
        if new_access_token is None:
            return

        cookie_params: CookieParams = getattr(
            request.state,
            REQUEST_STATE_COOKIE_PARAMS_KEY,
            CookieParams(secure=False),
        )
        cookie_header = self._make_cookie_header(
            value=new_access_token,
            is_secure=cookie_params.secure,
            samesite=cookie_params.samesite,
        )
        headers.append("Set-Cookie", cookie_header)
        log.debug("Cookie with access token '%s' was set.", new_access_token)

    def _maybe_delete_cookie(
        self,
        request: Request,
        headers: MutableHeaders,
    ) -> None:
        if not getattr(request.state, REQUEST_STATE_DELETE_ACCESS_TOKEN_KEY, False):
            return

        current_access_token = request.cookies.get(COOKIE_ACCESS_TOKEN_NAME)
        log.debug(
            "Deleting cookie with access token: '%s'.",
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
