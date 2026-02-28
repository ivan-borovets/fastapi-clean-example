from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.presentation.http.health.checks import db_check


class InternalServerError(Exception):
    pass


def make_health_router(*, debug_mode: bool) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/livez/",
        include_in_schema=False,
    )
    async def liveness_probe() -> str:
        return "OK"

    @router.get(
        "/healthz/",
        include_in_schema=False,
    )
    @inject
    async def readiness_probe(
        session: FromDishka[AsyncSession],
    ) -> str:
        await db_check(session)
        return "OK"

    if debug_mode:

        @router.get(
            "/http_error/",
            include_in_schema=False,
        )
        async def generate_http_error() -> None:
            raise InternalServerError("Internal Server Error")

    return router
