# Air Quality Ingestion Monitoring

This directory contains the complete observability setup for the air quality ingestion service, including metrics collection, logging, and dashboards.

## Overview

The monitoring stack includes:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Promtail**: Log collection
- **Kafka Exporter**: Kafka metrics
- **Node Exporter**: System metrics

## Services

### Metrics Collection

The ingestion service exposes the following metrics:

#### API Metrics
- `api_calls_total`: Number of API calls by city and status
- `api_call_duration_seconds`: API call latency
- `validation_errors_total`: Validation errors by city and pollutant

#### Processing Metrics
- `records_processed_total`: Total records processed by city and status
- `ingestion_rate_per_second`: Current ingestion rate by city
- `batch_size`: Batch processing size by city
- `processing_duration_seconds`: Processing time by city and stage

#### Error Tracking
- `errors_total`: Total errors by type and city
- `dead_letter_messages_total`: Messages sent to dead letter topic
- `mongo_operations_total`: MongoDB operations by operation and status

#### Kafka Metrics (Simulated)
- `kafka_consumer_lag`: Consumer lag by topic and partition
- `kafka_messages_processed_total`: Message throughput by topic

### Logging

The system implements structured logging with:

- **Error Classification**: Different error types are tracked and categorized
- **Context Information**: City, pollutant, and processing stage information
- **Performance Metrics**: Processing times and batch sizes
- **Dead Letter Handling**: Failed messages are logged and sent to dead letter topic

### Dead Letter Topic

Poisoned messages are handled through a dead letter mechanism:

- **Validation Errors**: Invalid data values
- **Processing Errors**: Data processing failures
- **API Errors**: External API failures
- **Storage Errors**: Database operation failures

## Accessing the Monitoring Stack

### Grafana Dashboards
- URL: http://localhost:3000
- Username: admin
- Password: admin

### Prometheus
- URL: http://localhost:9090
- Metrics endpoint: http://localhost:8000/metrics (ingestion service)

### Kafka UI
- URL: http://localhost:8080

## Running the Monitoring Stack

### Start All Services
```bash
docker-compose up -d
```

### Start Only Monitoring Services
```bash
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ingestion
```

## Configuration

### Prometheus Configuration
Edit `prometheus.yml` to modify scraping intervals, targets, or add new metrics sources.

### Grafana Dashboards
Dashboards are automatically provisioned from `grafana-dashboards/`. To add new dashboards:

1. Create a new JSON file in `grafana-dashboards/`
2. Restart the Grafana container

### Log Configuration
Log levels and formats can be adjusted in the ingestion service's `main.py` file.

## Monitoring Best Practices

1. **Alerting**: Set up alerts for high error rates, API timeouts, and processing failures
2. **Dashboards**: Monitor key metrics like ingestion rate, error rates, and processing latency
3. **Log Analysis**: Use Loki to search and analyze logs for debugging
4. **Capacity Planning**: Monitor batch sizes and processing times for scaling decisions

## Troubleshooting

### Common Issues

1. **Metrics Not Appearing**: Check that the ingestion service is running and accessible on port 8000
2. **Logs Not Showing**: Verify that Promtail is running and can access log files
3. **Dashboard Errors**: Check that Prometheus is scraping metrics correctly

### Useful Commands

```bash
# Check service health
docker-compose ps

# View service logs
docker-compose logs ingestion

# Test metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```
