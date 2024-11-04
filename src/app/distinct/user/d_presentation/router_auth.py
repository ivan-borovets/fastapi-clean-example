from fastapi import APIRouter

from app.distinct.user.scenarios.log_in.d_handler import log_in_router
from app.distinct.user.scenarios.log_out.d_handler import log_out_router
from app.distinct.user.scenarios.sign_up.d_handler import sign_up_router

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

auth_sub_routers = (
    sign_up_router,
    log_in_router,
    log_out_router,
)

for router in auth_sub_routers:
    auth_router.include_router(router)
