from typing import NewType

from sqlalchemy.ext.asyncio import AsyncSession

AuthAsyncSession = NewType("AuthAsyncSession", AsyncSession)
