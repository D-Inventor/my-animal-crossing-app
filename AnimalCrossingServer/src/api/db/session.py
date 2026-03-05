from typing import AsyncGenerator

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.db.config import DatabaseSettings


def set_engine(
    app: FastAPI, engine: AsyncEngine, session_maker: async_sessionmaker[AsyncSession]
) -> None:
    app.state["_engine"] = engine
    app.state["_session_local"] = session_maker


def get_engine(app: FastAPI) -> AsyncEngine:
    if not hasattr(app.state, "_engine") or not isinstance(
        app.state["_engine"], AsyncEngine
    ):
        raise ValueError("The engine is not configured.")

    return app.state["_engine"]


def get_engine_from_configuration() -> AsyncEngine:
    return create_async_engine(DatabaseSettings().get_connection_url(), echo=False)


def get_sessionmaker_for_app(app: FastAPI) -> async_sessionmaker[AsyncSession]:
    if not hasattr(app.state, "_session_local") or not isinstance(
        app.state["_session_local"], async_sessionmaker
    ):
        raise ValueError(
            "Cannot get sessionmaker, because no session was set on the app"
        )

    return app.state["_session_local"]


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_local = get_sessionmaker_for_app(request.app)
    session = session_local()
    try:
        yield session
    finally:
        await session.close()
