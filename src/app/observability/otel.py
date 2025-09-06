from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from ..config import settings




def init_otel():
    resource = Resource.create({
    "service.name": settings.service_name,
    "deployment.environment": settings.environment,
    })
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{settings.otlp_endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)




def get_tracer():
    return trace.get_tracer(__name__)