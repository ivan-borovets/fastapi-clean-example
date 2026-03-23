import asyncio

import dishka.plotter
from dishka import AsyncContainer

from app.main.run import make_app


def generate_d2_dependency_graph(container: AsyncContainer) -> str:
    """
    Generates dependency graph for container in `d2` format.
    See https://d2lang.com for rendering instructions.
    """
    return dishka.plotter.render_d2(container)


async def main() -> None:
    app = make_app()
    container = app.state.dishka_container
    try:
        print(generate_d2_dependency_graph(container))
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
