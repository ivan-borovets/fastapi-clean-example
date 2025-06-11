from fastapi import APIRouter

from app.presentation.http.controllers.general.healthcheck import healthcheck_router

general_router = APIRouter(
    tags=["General"],
)
general_sub_routers: tuple[APIRouter, ...] = (healthcheck_router,)

for router in general_sub_routers:
    general_router.include_router(router)
