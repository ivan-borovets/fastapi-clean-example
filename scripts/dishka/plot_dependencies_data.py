import dishka.plotter
from dishka import AsyncContainer, make_async_container

from app.setup.config.settings import Settings
from app.setup.ioc.ioc_registry import get_providers


def make_container(settings: Settings) -> AsyncContainer:
    return make_async_container(*get_providers(), context={Settings: settings})


def generate_dependency_graph_d2(container: AsyncContainer) -> str:
    """
    Generates a dependency graph for the container in `d2` format.
    See https://d2lang.com for rendering instructions.
    """
    return dishka.plotter.render_d2(container)


if __name__ == "__main__":
    settings: Settings = Settings.from_file()
    container: AsyncContainer = make_container(settings)
    print(generate_dependency_graph_d2(container))
