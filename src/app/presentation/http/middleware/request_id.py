import uuid

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.application.common.services.request_id import set_request_id

REQUEST_ID_HEADER = "X-Request-Id"


class ASGIRequestIdMiddleware:
    def __init__(self, app: ASGIApp, header_name: str = REQUEST_ID_HEADER) -> None:
        self.app = app
        self._header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        request_id = request.headers.get(self._header_name)
        if not request_id:
            request_id = str(uuid.uuid4())

        set_request_id(request_id)
        request.state.request_id = request_id

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers[self._header_name] = request_id
            await send(message)

        return await self.app(scope, receive, send_wrapper)
