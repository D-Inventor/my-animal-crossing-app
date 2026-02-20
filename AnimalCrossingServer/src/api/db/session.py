from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.db.config import DatabaseSettings


def _create_engine_for_app(request: Request) -> AsyncEngine:
    # Prefer an engine cached on app.state to avoid recreating per request
    app = request.app
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


def _create_session_for_app(request: Request) -> async_sessionmaker:
    app = request.app
    if hasattr(app.state, "_session_local") and isinstance(
        app.state._session_local, async_sessionmaker
    ):
        return app.state._session_local

    engine = _create_engine_for_app(request)
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    app.state._session_local = session_local
    return session_local


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_local = _create_session_for_app(request)
    session = session_local()
    try:
        yield session
    finally:
        await session.close()
