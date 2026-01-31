from fastapi import APIRouter

from app.presentation.http.controllers.general.health import (
    create_health_router,
)
from app.presentation.http.controllers.general.version import (
    create_version_router,
)


def create_general_router() -> APIRouter:
    router = APIRouter(tags=["General"])
    router.include_router(create_health_router())
    router.include_router(create_version_router())
    return router
