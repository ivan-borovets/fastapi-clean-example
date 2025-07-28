from fastapi import APIRouter
from starlette.requests import Request

healthcheck_router = APIRouter()


@healthcheck_router.get("/")
async def healthcheck(_: Request) -> dict[str, str]:
    """
    - Open to everyone.
    - Returns `200 OK` if the API is alive.
    """
    return {"status": "ok"}
