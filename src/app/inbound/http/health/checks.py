from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ProbeError(Exception):
    pass


async def db_check(session: AsyncSession) -> None:
    try:
        await session.scalar(text("SELECT 1"))
    except Exception as e:
        raise ProbeError from e
