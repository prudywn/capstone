from prometheus_client import Counter, start_http_server

API_CALLS = Counter("api_calls_total", "Number of API calls", ["city", "status"])  # status = success/fail
VALIDATION_ERRORS = Counter("validation_errors_total", "Validation errors count", ["city"])
MONGO_OPS = Counter("mongo_operations_total", "MongoDB ops count", ["operation", "status"])

def start_metrics_server(port=8000):
    start_http_server(port)
