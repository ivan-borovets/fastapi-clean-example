# pylint: disable=C0301 (line-too-long)

from dishka import Provider, Scope, from_context, provide
from starlette.requests import Request

from app.distinct.user.b_application.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)
from app.distinct.user.d_presentation.adapters.access_token_request_handler_cookie import (
    CookieAccessTokenRequestHandler,
)


class UserPresentationProvider(Provider):
    request = from_context(provides=Request, scope=Scope.REQUEST)

    access_token_request_handler = provide(
        source=CookieAccessTokenRequestHandler,
        scope=Scope.REQUEST,
        provides=AccessTokenRequestHandler,
    )
