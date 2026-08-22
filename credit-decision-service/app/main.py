import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.api.routes import decisions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - trace_id=%(otelTraceID)s",
    force=True
)

# OpenTelemetry tracing setup
resource = Resource(attributes={"service.name": "credit-decision-service"})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="tempo.monitoring.svc.cluster.local:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)

LoggingInstrumentor().instrument(set_logging_format=False)
RequestsInstrumentor().instrument()

app = FastAPI(title="Credit Decision Service", version="1.0.0")

FastAPIInstrumentor.instrument_app(app)

# Disable Prometheus instrumentation during tests.
# It currently conflicts with the router structure used by this service.
if os.getenv("TESTING") != "true":
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decisions.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "credit-decision-service"}
