from flask import Flask, jsonify, Response, request
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import os
import time
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

app = Flask(__name__)

resource = Resource.create({
    "service.name": os.environ.get("OTEL_SERVICE_NAME", "flask-metrics-app")
})

trace.set_tracer_provider(TracerProvider(resource=resource))

otlp_exporter = OTLPSpanExporter(
    endpoint=os.environ.get(
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        "http://tempo:4318/v1/traces"
    )
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

FlaskInstrumentor().instrument_app(app)

APP_ENV = os.environ.get("APP_ENV", "development")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
API_KEY = os.environ.get("API_KEY", "missing")

HTTP_REQUESTS_TOTAL = Counter(
    "flask_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

BUSINESS_REQUESTS_TOTAL = Counter(
    "flask_business_requests_total",
    "Total number of business requests"
)

IN_PROGRESS_REQUESTS = Gauge(
    "flask_in_progress_requests",
    "Number of requests currently being processed"
)

@app.before_request
def before_request():
    request.start_time = time.time()
    IN_PROGRESS_REQUESTS.inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time

    endpoint = request.endpoint or "unknown"

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(duration)

    IN_PROGRESS_REQUESTS.dec()

    return response

@app.route("/")
def home():
    BUSINESS_REQUESTS_TOTAL.inc()

    return jsonify({
        "api_key_loaded": API_KEY != "missing",
        "app_env": APP_ENV,
        "log_level": LOG_LEVEL,
        "message": "Hello from Flask with Prometheus metrics!",
        "status": "running"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
