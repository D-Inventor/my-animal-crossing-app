import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.config import DatabaseSettings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def create_engine() -> AsyncGenerator[async_sessionmaker, Any, None]:
    engine = create_async_engine(DatabaseSettings().get_connection_url(), echo=False)
    logger.debug("Engine created")
    yield async_sessionmaker(bind=engine, expire_on_commit=False)

    await engine.dispose()
    logger.debug("Engine disposed")


@asynccontextmanager
async def create_session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, Any, None]:
    async with session_maker() as session:
        logger.debug("Session created")
        yield session
    logger.debug("Session disposed")
