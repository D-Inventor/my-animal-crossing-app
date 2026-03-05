from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from api.db.villager import Base


@pytest.fixture
async def mariadb_session(
    mariadb_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:

    async with mariadb_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(bind=mariadb_engine, expire_on_commit=False)
