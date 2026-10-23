from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def make_async_engine(
    *,
    dsn: str,
    echo: bool,
    echo_pool: bool,
    pool_size: int,
    max_overflow: int,
    connect_timeout_s: int,
) -> AsyncEngine:
    return create_async_engine(
        url=dsn,
        echo=echo,
        echo_pool=echo_pool,
        hide_parameters=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        connect_args={"connect_timeout": connect_timeout_s},
        pool_pre_ping=True,
    )


def make_async_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
