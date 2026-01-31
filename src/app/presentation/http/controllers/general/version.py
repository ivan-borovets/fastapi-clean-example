from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict

from app.application.queries.get_app_version import GetAppVersionQueryService


class VersionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str


def create_version_router() -> APIRouter:
    router = APIRouter()

    @router.get(
        "/version",
        description=getdoc(GetAppVersionQueryService),
        response_model=VersionResponse,
        status_code=status.HTTP_200_OK,
    )
    @inject
    async def get_version(
        interactor: FromDishka[GetAppVersionQueryService],
    ) -> VersionResponse:
        result = await interactor.execute()
        return VersionResponse(version=result.version)

    return router
