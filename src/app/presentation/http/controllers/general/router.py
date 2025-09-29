from fastapi import APIRouter

from app.presentation.http.controllers.general.health import (
    create_health_router,
)


def create_general_router() -> APIRouter:
    router = APIRouter(
        tags=["General"],
    )

    sub_routers = (create_health_router(),)

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router
