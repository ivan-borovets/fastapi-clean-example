import asyncio

import dishka.plotter

from app.main.run import make_app


async def main() -> None:
    """
    Generates dependency graph for container in `d2` format.
    See https://d2lang.com for rendering instructions.
    """
    app = make_app()
    container = app.state.dishka_container
    try:
        print(dishka.plotter.render_d2(container))
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
