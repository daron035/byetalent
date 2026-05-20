from collections.abc import AsyncGenerator

import orjson

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.persistence.postgres.config import PostgresConfig


async def build_sa_engine(cfg: PostgresConfig) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        cfg.full_url,
        echo_pool="debug",
        json_serializer=lambda data: orjson.dumps(data).decode(),
        json_deserializer=orjson.loads,
        pool_size=50,
        isolation_level="READ COMMITTED",
    )
    yield engine

    await engine.dispose()


def build_sa_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    session_factory = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return session_factory


async def build_sa_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session
