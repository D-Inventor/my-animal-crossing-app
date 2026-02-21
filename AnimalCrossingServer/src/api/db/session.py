from typing import AsyncGenerator, Protocol

from fastapi import FastAPI, Request
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.db.config import DatabaseSettings


class DatabaseState(Protocol):
    _engine: AsyncEngine | None
    _session_local: async_sessionmaker[AsyncSession] | None
    database_url: URL | None


def get_engine_for_app(app: FastAPI) -> AsyncEngine:
    # The app will use a single engine instance for it's entire lifetime.
    # It is stored on the app.state so that we can overwrite it in tests
    if hasattr(app.state, "_engine") and isinstance(app.state._engine, AsyncEngine):
        return app.state._engine

    database_url = (
        getattr(app.state, "database_url", None)
        or DatabaseSettings().get_connection_url()
    )
    if not isinstance(database_url, URL):
        raise RuntimeError("DATABASE_URL not configured on app.state or environment")

    engine = create_async_engine(database_url, echo=False)
    app.state._engine = engine
    return engine


def get_sessionmaker_for_app(app: FastAPI) -> async_sessionmaker[AsyncSession]:
    if hasattr(app.state, "_session_local") and isinstance(
        app.state._session_local, async_sessionmaker
    ):
        return app.state._session_local

    engine = get_engine_for_app(app)
    session_local = async_sessionmaker[AsyncSession](
        bind=engine, expire_on_commit=False
    )
    app.state._session_local = session_local
    return session_local


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_local = get_sessionmaker_for_app(request.app)
    session = session_local()
    try:
        yield session
    finally:
        await session.close()
