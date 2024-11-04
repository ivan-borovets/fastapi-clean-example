from dishka import AsyncContainer, Provider
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.presentation.common.http_api_routers.root import root_router
from app.setup.app_factory import configure_app, create_app, create_async_ioc_container
from app.setup.config.logs import configure_logging
from app.setup.config.settings import Settings
from app.setup.ioc.registry import get_providers


def make_app(
    *di_providers: Provider,
    settings: Settings | None = None,
) -> FastAPI:
    if not settings:
        settings = Settings.from_file()

    configure_logging(level=settings.logging.level)

    app: FastAPI = create_app()
    configure_app(app=app, root_router=root_router)

    async_ioc_container: AsyncContainer = create_async_ioc_container(
        providers=(*get_providers(), *di_providers),
        settings=settings,
    )
    setup_dishka(container=async_ioc_container, app=app)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=make_app(),
        port=8000,
        reload=False,
        loop="uvloop",
    )
