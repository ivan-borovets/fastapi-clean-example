import dishka.plotter
import uvloop
from dishka import AsyncContainer, make_async_container

from app.setup.config.settings import AppSettings, load_settings
from app.setup.ioc.provider_registry import get_providers


def make_plot_data_container(settings: AppSettings) -> AsyncContainer:
    return make_async_container(*get_providers(), context={AppSettings: settings})


def generate_dependency_graph_d2(container: AsyncContainer) -> str:
    """
    Generates a dependency graph for the container in `d2` format.
    See https://d2lang.com for rendering instructions.
    """
    return dishka.plotter.render_d2(container)


async def main() -> None:
    settings: AppSettings = load_settings()
    async with make_plot_data_container(settings)() as container:
        print(generate_dependency_graph_d2(container))
        await container.close()


if __name__ == "__main__":
    uvloop.run(main())
