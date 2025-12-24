import asyncio
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pytest

from app.infrastructure.adapters.password_hasher_bcrypt import BcryptPasswordHasher
from app.infrastructure.adapters.types import HasherSemaphore, HasherThreadPoolExecutor


@pytest.fixture(scope="session")
def hasher_max_threads() -> int:
    return 4


@pytest.fixture(scope="session")
def hasher_threadpool_executor(
    hasher_max_threads: int,
) -> Iterator[HasherThreadPoolExecutor]:
    executor = HasherThreadPoolExecutor(
        ThreadPoolExecutor(max_workers=hasher_max_threads)
    )
    yield executor
    executor.shutdown(wait=True, cancel_futures=True)


@pytest.fixture
def hasher_semaphore(hasher_max_threads: int) -> HasherSemaphore:
    return HasherSemaphore(asyncio.Semaphore(hasher_max_threads))


@pytest.fixture
def bcrypt_password_hasher(
    hasher_threadpool_executor: HasherThreadPoolExecutor,
    hasher_semaphore: HasherSemaphore,
) -> partial[BcryptPasswordHasher]:
    return partial(
        BcryptPasswordHasher,
        work_factor=11,
        pepper=b"Habanero",
        executor=hasher_threadpool_executor,
        semaphore=hasher_semaphore,
        semaphore_wait_timeout_s=3,
    )
