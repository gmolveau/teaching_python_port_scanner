import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def is_enabled() -> bool:
    return os.environ.get("OTEL_ENABLED", "false").lower() in ("true", "1", "yes")


def configure_telemetry() -> None:
    if not is_enabled():
        return

    service_name = os.environ.get("OTEL_SERVICE_NAME", "port-scanner")
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    resource = Resource(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
