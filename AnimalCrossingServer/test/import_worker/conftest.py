import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from import_worker.db.snapshot import Base


@pytest.fixture
async def session_maker(mariadb_engine):
    async with mariadb_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(bind=mariadb_engine, expire_on_commit=False)
