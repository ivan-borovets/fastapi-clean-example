from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.presentation.http.controllers.api_v1_router import api_v1_router

root_router = APIRouter()


@root_router.get("/", tags=["General"])
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="docs/")


root_sub_routers: tuple[APIRouter, ...] = (api_v1_router,)

for router in root_sub_routers:
    root_router.include_router(router)
