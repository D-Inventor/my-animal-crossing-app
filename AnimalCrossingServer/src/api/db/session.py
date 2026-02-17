from typing import Generator

from fastapi import Request
from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def _create_engine_for_app(request: Request) -> Engine:
    # Prefer an engine cached on app.state to avoid recreating per request
    app = request.app
    if hasattr(app.state, "_engine") and isinstance(app.state._engine, Engine):
        return app.state._engine

    database_url = getattr(app.state, "database_url", None)
    if not isinstance(database_url, URL):
        raise RuntimeError("DATABASE_URL not configured on app.state or environment")

    engine = create_engine(database_url, echo=False)
    app.state._engine = engine
    return engine


def _create_session_for_app(request: Request) -> sessionmaker:
    app = request.app
    if hasattr(app.state, "_session_local") and isinstance(
        app.state._session_local, sessionmaker
    ):
        return app.state._session_local

    engine = _create_engine_for_app(request)
    session_local = sessionmaker(bind=engine, expire_on_commit=False)
    app.state._session_local = session_local
    return session_local


def get_session(request: Request) -> Generator[Session, None, None]:
    session_local = _create_session_for_app(request)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
