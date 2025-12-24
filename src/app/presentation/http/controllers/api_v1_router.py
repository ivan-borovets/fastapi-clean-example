from fastapi import APIRouter

from app.presentation.http.controllers.account.router import create_account_router
from app.presentation.http.controllers.general.router import create_general_router
from app.presentation.http.controllers.users.router import create_users_router


def create_api_v1_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1")
    router.include_router(create_account_router())
    router.include_router(create_general_router())
    router.include_router(create_users_router())
    return router
