from fastapi import APIRouter
from starlette.requests import Request


def create_healthcheck_router() -> APIRouter:
    router = APIRouter()

    @router.get("/")
    async def healthcheck(_: Request) -> dict[str, str]:
        """
        - Open to everyone.
        - Returns `200 OK` if the API is alive.
        """
        return {"status": "ok"}

    return router
