from typing import ClassVar, Literal, cast

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.outbound.auth_ctx.cookie_manager import STAGED_COOKIE


class AuthCookieMiddleware(BaseHTTPMiddleware):
    MISSING: ClassVar[object] = object()

    def __init__(
        self,
        app: ASGIApp,
        *,
        cookie_name: str,
        cookie_path: str,
        cookie_httponly: bool,
        cookie_secure: bool,
        cookie_samesite: Literal["lax", "strict", "none"],
    ) -> None:
        super().__init__(app)
        self._cookie_name = cookie_name
        self._cookie_path = cookie_path
        self._cookie_httponly = cookie_httponly
        self._cookie_secure = cookie_secure
        self._cookie_samesite = cookie_samesite

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)

        staged = getattr(request.state, STAGED_COOKIE, self.MISSING)
        if staged is self.MISSING:
            return response

        value = cast(str | None, staged)
        if value is None:
            response.delete_cookie(
                key=self._cookie_name,
                path=self._cookie_path,
            )
            return response

        response.set_cookie(
            key=self._cookie_name,
            value=value,
            path=self._cookie_path,
            httponly=self._cookie_httponly,
            secure=self._cookie_secure,
            samesite=self._cookie_samesite,
        )
        return response
