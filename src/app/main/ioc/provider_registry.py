from collections.abc import Iterable

from dishka import Provider

from app.main.ioc.core import CoreProvider
from app.main.ioc.outbound import outbound_providers


def get_providers() -> Iterable[Provider]:
    return (
        CoreProvider(),
        *outbound_providers(),
    )
