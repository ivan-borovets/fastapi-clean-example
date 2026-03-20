from collections.abc import Iterable

from dishka import Provider

from app.main.ioc.core import CoreProvider
from app.main.ioc.infrastructure import infrastructure_providers


def get_providers() -> Iterable[Provider]:
    return (
        CoreProvider(),
        *infrastructure_providers(),
    )
