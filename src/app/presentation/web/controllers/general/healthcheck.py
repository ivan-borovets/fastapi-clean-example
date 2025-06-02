from fastapi import APIRouter
from starlette.requests import Request

healthcheck_router = APIRouter()


@healthcheck_router.get("/")
async def healthcheck(_: Request) -> dict[str, str]:
    return {"status": "ok"}
