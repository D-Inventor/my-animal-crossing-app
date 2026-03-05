from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api.db.dependencies import get_engine
from api.telemetry.config import TelemetryConfig


def telemetry_lifespan(app: FastAPI) -> None:

    config = TelemetryConfig()
    if not config.enabled:
        return

    resource = Resource.create({SERVICE_NAME: "animal-crossing-api"})

    trace_provider = TracerProvider(resource=resource)
    trace_processor = BatchSpanProcessor(config.get_trace_exporter())
    trace_provider.add_span_processor(trace_processor)
    trace.set_tracer_provider(trace_provider)

    metric_reader = PeriodicExportingMetricReader(config.get_metric_exporter())
    metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(metric_provider)

    FastAPIInstrumentor.instrument_app(app)
    AsyncioInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=get_engine(app).sync_engine)
