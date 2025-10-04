import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import NewType

from sqlalchemy.ext.asyncio import AsyncSession

MainAsyncSession = NewType("MainAsyncSession", AsyncSession)
HasherThreadPoolExecutor = NewType("HasherThreadPoolExecutor", ThreadPoolExecutor)
HasherSemaphore = NewType("HasherSemaphore", asyncio.Semaphore)
