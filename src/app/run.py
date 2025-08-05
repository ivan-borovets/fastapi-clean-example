from dishka import Provider
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.presentation.http.controllers.root_router import create_root_router
from app.setup.app_factory import configure_app, create_app, create_async_ioc_container
from app.setup.config.logs import configure_logging
from app.setup.config.settings import AppSettings, load_settings
from app.setup.ioc.provider_registry import get_providers


def make_app(
    *di_providers: Provider,
    settings: AppSettings | None = None,
) -> FastAPI:
    if settings is None:
        configure_logging()
        settings = load_settings()

    configure_logging(level=settings.logs.level)

    app: FastAPI = create_app()
    configure_app(app=app, root_router=create_root_router())

    async_ioc_container = create_async_ioc_container(
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
