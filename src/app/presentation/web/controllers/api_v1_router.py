from fastapi import APIRouter

from app.presentation.web.controllers.account.router import account_router
from app.presentation.web.controllers.general.router import general_router
from app.presentation.web.controllers.users.router import users_router

api_v1_router = APIRouter(
    prefix="/api/v1",
)


api_v1_sub_routers: tuple[APIRouter, ...] = (
    account_router,
    general_router,
    users_router,
)

for router in api_v1_sub_routers:
    api_v1_router.include_router(router)
