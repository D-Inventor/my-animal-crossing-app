from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.db.session import get_engine_for_app


class TelemetryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TELEMETRY_")
    enabled: bool = Field(False)
    exporter_endpoint: str | None = Field(None)

    def get_exporter(self) -> OTLPSpanExporter:
        if self.exporter_endpoint is None:
            raise ValueError(
                "TELEMETRY_EXPORTER_ENDPOINT must be set when telemetry is enabled."
            )

        return OTLPSpanExporter(endpoint=self.exporter_endpoint)


def configure_telemetry(app: FastAPI) -> None:

    config = TelemetryConfig()
    if not config.enabled:
        return

    resource = Resource.create({SERVICE_NAME: "animal-crossing-api"})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(config.get_exporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    AsyncioInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=get_engine_for_app(app).sync_engine)
