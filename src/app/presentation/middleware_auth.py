import logging
from typing import Any, Literal

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response: Response = await call_next(request)

        new_access_token: str | None = getattr(request.state, "new_access_token", None)
        cookie_params: dict[str, Any] = getattr(request.state, "cookie_params", {})
        cookie_params_secure: bool | None = cookie_params.get("secure")
        cookie_params_samesite: Literal["strict", "none"] | None = cookie_params.get(
            "samesite"
        )

        if new_access_token is not None and cookie_params_secure is not None:
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=cookie_params_secure,
                samesite=cookie_params_samesite,
            )
            log.info("Cookie with access token '%s' was set.", new_access_token)

        is_delete_token: bool = getattr(request.state, "delete_access_token", False)
        if is_delete_token:
            response.delete_cookie(key="access_token")
            access_token: str | None = getattr(request.state, "access_token", None)
            if access_token is None:
                log.info("Cookie with access token was already deleted.")
            else:
                log.info("Cookie with access token '%s' was deleted.", access_token)

        return response
