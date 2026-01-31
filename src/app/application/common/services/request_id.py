from contextvars import ContextVar

_request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

def set_request_id(request_id: str) -> None:
    _request_id_var.set(request_id)

def get_request_id() -> str | None:
    return _request_id_var.get()

class RequestIdService:
    def get_current_request_id(self) -> str | None:
        return get_request_id()
