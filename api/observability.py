from __future__ import annotations

import logging
import os
from typing import Any

LOGGER = logging.getLogger("tcria.mcp")


def configure_logging() -> None:
    level = os.getenv("TCRIA_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def configure_tracing(app: Any, service_name: str = "tcria-mcp-gateway") -> dict[str, Any]:
    """Configure OpenTelemetry when optional dependencies are installed.

    The gateway must remain importable even when OpenTelemetry packages are not
    present. This helper therefore treats tracing as an optional production add-on.
    """
    enabled = os.getenv("TCRIA_OTEL_ENABLED", "false").lower() in {"1", "true", "yes"}
    if not enabled:
        return {"enabled": False, "reason": "disabled"}

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except Exception as exc:  # pragma: no cover - optional dependency path
        LOGGER.warning("OpenTelemetry requested but unavailable: %s", exc)
        return {"enabled": False, "reason": "missing_optional_dependencies", "error": str(exc)}

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint) if endpoint else OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    return {"enabled": True, "service_name": service_name, "endpoint": endpoint}
