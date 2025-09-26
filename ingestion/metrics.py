from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import logging

# API and external service metrics
API_CALLS = Counter("api_calls_total", "Number of API calls", ["city", "status"])  # status = success/fail
API_LATENCY = Histogram("api_call_duration_seconds", "API call duration", ["city"])
VALIDATION_ERRORS = Counter("validation_errors_total", "Validation errors count", ["city", "pollutant"])
MONGO_OPS = Counter("mongo_operations_total", "MongoDB ops count", ["operation", "status"])

# Ingestion metrics
INGESTION_RATE = Gauge("ingestion_rate_per_second", "Current ingestion rate", ["city"])
RECORDS_PROCESSED = Counter("records_processed_total", "Total records processed", ["city", "status"])
BATCH_SIZE = Histogram("batch_size", "Batch processing size", ["city"])

# Error tracking
ERRORS = Counter("errors_total", "Total errors", ["error_type", "city"])
DEAD_LETTER_MESSAGES = Counter("dead_letter_messages_total", "Messages sent to dead letter topic", ["topic", "reason"])

# Kafka metrics (simulated for now - would be real in production)
KAFKA_LAG = Gauge("kafka_consumer_lag", "Kafka consumer lag", ["topic", "partition"])
KAFKA_THROUGHPUT = Counter("kafka_messages_processed_total", "Kafka messages processed", ["topic"])

# Processing time metrics
PROCESSING_TIME = Histogram("processing_duration_seconds", "Processing duration", ["city", "stage"])

def start_metrics_server(port=8000):
    start_http_server(port)
    logging.info(f"Metrics server started on port {port}")

def record_api_call(city, success, duration):
    """Record API call metrics"""
    status = "success" if success else "fail"
    API_CALLS.labels(city=city, status=status).inc()
    if success:
        API_LATENCY.labels(city=city).observe(duration)

def record_validation_error(city, pollutant):
    """Record validation error"""
    VALIDATION_ERRORS.labels(city=city, pollutant=pollutant).inc()
    ERRORS.labels(error_type="validation", city=city).inc()

def record_mongo_operation(operation, success):
    """Record MongoDB operation"""
    status = "success" if success else "fail"
    MONGO_OPS.labels(operation=operation, status=status).inc()
    if not success:
        ERRORS.labels(error_type="mongo", city="unknown").inc()

def record_processing_time(city, stage, duration):
    """Record processing time for different stages"""
    PROCESSING_TIME.labels(city=city, stage=stage).observe(duration)

def record_records_processed(city, count, success=True):
    """Record number of records processed"""
    status = "success" if success else "fail"
    RECORDS_PROCESSED.labels(city=city, status=status).inc(count)
    INGESTION_RATE.labels(city=city).set(count)

def record_dead_letter_message(topic, reason):
    """Record message sent to dead letter topic"""
    DEAD_LETTER_MESSAGES.labels(topic=topic, reason=reason).inc()
    ERRORS.labels(error_type="dead_letter", city="unknown").inc()

def update_kafka_lag(topic, partition, lag):
    """Update Kafka consumer lag"""
    KAFKA_LAG.labels(topic=topic, partition=partition).set(lag)

def record_kafka_throughput(topic, count=1):
    """Record Kafka message throughput"""
    KAFKA_THROUGHPUT.labels(topic=topic).inc(count)
