import uvicorn
from fastapi import FastAPI

from app.setup.app_factory import create_app_with_container
from app.setup.config.logs import configure_logging
from app.setup.config.settings import Settings


def main() -> None:
    settings: Settings = Settings.from_file()
    configure_logging(level=settings.logging.level)
    app: FastAPI = create_app_with_container(settings)
    uvicorn.run(
        app=app,
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        loop="uvloop",
    )


if __name__ == "__main__":
    main()
