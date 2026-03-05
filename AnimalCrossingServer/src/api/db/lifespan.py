from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.db.config import DatabaseSettings


def engine_lifespan_from_configuration() -> AsyncEngine:
    return create_async_engine(DatabaseSettings().get_connection_url(), echo=False)


def set_engine(
    app: FastAPI, engine: AsyncEngine, session_maker: async_sessionmaker[AsyncSession]
) -> None:
    app.state["_engine"] = engine
    app.state["_session_local"] = session_maker
