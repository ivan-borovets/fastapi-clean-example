from typing import NewType

from sqlalchemy.ext.asyncio import AsyncSession

MainAsyncSession = NewType("MainAsyncSession", AsyncSession)
