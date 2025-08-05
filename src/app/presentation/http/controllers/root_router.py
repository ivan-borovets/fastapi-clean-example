from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.presentation.http.controllers.api_v1_router import create_api_v1_router


def create_root_router() -> APIRouter:
    router = APIRouter()

    @router.get("/", tags=["General"])
    async def redirect_to_docs() -> RedirectResponse:
        """
        - Open to everyone.
        - Redirects to Swagger documentation.
        """
        return RedirectResponse(url="docs/")

    sub_routers = (create_api_v1_router(),)

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router
