from typing import NewType

from sqlalchemy.ext.asyncio import AsyncSession

# database
UserAsyncSession = NewType("UserAsyncSession", AsyncSession)
