from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pytest

from app.infrastructure.adapters.password_hasher_bcrypt import BcryptPasswordHasher
from app.infrastructure.adapters.types import HasherThreadPoolExecutor


@pytest.fixture(scope="session")
def hasher_threadpool_executor() -> Iterable[HasherThreadPoolExecutor]:
    executor = HasherThreadPoolExecutor(ThreadPoolExecutor(max_workers=4))
    yield executor
    executor.shutdown(wait=True, cancel_futures=True)


@pytest.fixture
def bcrypt_password_hasher(
    hasher_threadpool_executor: HasherThreadPoolExecutor,
) -> partial[BcryptPasswordHasher]:
    return partial(
        BcryptPasswordHasher,
        executor=hasher_threadpool_executor,
        pepper="Habanero",
        work_factor=11,
    )
