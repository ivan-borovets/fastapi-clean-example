import asyncio

import dishka.plotter
from dishka import AsyncContainer

from app.config.loader import (
    load_app_settings,
    load_cookie_settings,
    load_jwt_settings,
    load_password_hasher_settings,
    load_postgres_settings,
    load_session_settings,
    load_sqla_settings,
)
from app.main.run import make_ioc_container


def generate_dependency_graph_d2(container: AsyncContainer) -> str:
    """
    Generates a dependency graph for the container in `d2` format.
    See https://d2lang.com for rendering instructions.
    """
    return dishka.plotter.render_d2(container)


async def main() -> None:
    async with make_ioc_container(
        app_settings=load_app_settings(),
        postgres_settings=load_postgres_settings(),
        sqla_settings=load_sqla_settings(),
        password_hasher_settings=load_password_hasher_settings(),
        jwt_settings=load_jwt_settings(),
        session_settings=load_session_settings(),
        cookie_settings=load_cookie_settings(),
    )() as container:
        print(generate_dependency_graph_d2(container))
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
