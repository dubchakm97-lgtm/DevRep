from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os

app = Flask(__name__)

APP_ENV = os.environ.get("APP_ENV", "development")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
API_KEY = os.environ.get("API_KEY", "missing")

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint"]
)

@app.before_request
def before_request():
    from flask import request
    REQUEST_COUNT.labels(request.method, request.path).inc()

@app.route("/")
def home():
    return jsonify({
        "message": "Hello from Flask with Prometheus metrics!",
        "status": "running",
        "app_env": APP_ENV,
        "log_level": LOG_LEVEL,
        "api_key_loaded": API_KEY != "missing"
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
