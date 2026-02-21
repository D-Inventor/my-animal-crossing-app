"""Workspace-local start module for the API (FastAPI).

This module lives inside the `api` package so editors and tooling can find
it.
"""

from opentelemetry import trace
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from api.db.session import get_engine_for_app

from .app import app


def main() -> None:
    try:
        import uvicorn

        configure_telemetry()

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Error running uvicorn: {e}")
        print("uvicorn not installed. Install with: pip install fastapi uvicorn")


def configure_telemetry() -> None:
    provider = TracerProvider()
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    AsyncioInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=get_engine_for_app(app).sync_engine)


if __name__ == "__main__":
    main()
