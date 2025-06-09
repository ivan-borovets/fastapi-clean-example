from dishka import Provider, Scope, from_context, provide_all
from starlette.requests import Request

from app.presentation.web.adapters.jwt_access_token_processor import (
    JwtAccessTokenProcessor,
)


class PresentationProvider(Provider):
    scope = Scope.REQUEST

    request = from_context(provides=Request)

    # Concrete Objects
    presentation_objects = provide_all(
        JwtAccessTokenProcessor,
    )
