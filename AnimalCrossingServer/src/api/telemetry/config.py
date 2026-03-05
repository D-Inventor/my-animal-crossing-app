from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelemetryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TELEMETRY_")
    enabled: bool = Field(False)
    exporter_endpoint: str | None = Field(None)

    def get_trace_exporter(self) -> OTLPSpanExporter:
        if self.exporter_endpoint is None:
            raise ValueError(
                "TELEMETRY_EXPORTER_ENDPOINT must be set when telemetry is enabled."
            )

        return OTLPSpanExporter(endpoint=self.exporter_endpoint)

    def get_metric_exporter(self) -> OTLPMetricExporter:
        if self.exporter_endpoint is None:
            raise ValueError(
                "TELEMETRY_EXPORTER_ENDPOINT must be set when telemetry is enabled."
            )

        return OTLPMetricExporter(endpoint=self.exporter_endpoint)
