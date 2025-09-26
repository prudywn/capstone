# Air Quality Ingestion Observability Testing Guide

This guide provides step-by-step instructions to test the complete observability setup for the air quality ingestion service.

## Prerequisites

- Docker and Docker Compose installed
- Terminal/Command line access
- Web browser

## Step 1: Start All Services

```bash
cd /home/prudy/capstone
docker-compose up -d
```

**Expected Output:**
```
Creating network "capstone_default" with the default driver
Creating volume "capstone_mongo-data" with default driver
Creating volume "capstone_cassandra-data" with default driver
Creating volume "capstone_prometheus-data" with default driver
Creating volume "capstone_grafana-data" with default driver
Creating volume "capstone_loki-data" with default driver
Creating zookeeper ... done
Creating mongo ... done
Creating cassandra ... done
Creating kafka ... done
Creating schema-registry ... done
Creating prometheus ... done
Creating grafana ... done
Creating kafka-exporter ... done
Creating node-exporter ... done
Creating loki ... done
Creating promtail ... done
Creating kafka-dead-letter ... done
Creating ingestion ... done
Creating storage ... done
Creating kafka-ui ... done
```

## Step 2: Verify All Services Are Running

```bash
docker-compose ps
```

**Expected Output:** All services should show "Up" status. Wait a few minutes for all services to fully start.

## Step 3: Test Basic Service Connectivity

### 3.1 Test Ingestion Service Health
```bash
curl -s http://localhost:8000/metrics | head -20
```

**Expected Output:**
```
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="11",patchlevel="7",version="3.11.7"} 1.0
# HELP api_calls_total Number of API calls
# TYPE api_calls_total counter
```

### 3.2 Test Prometheus Connectivity
```bash
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health == "up") | .labels.job'
```

**Expected Output:**
```
"prometheus"
"ingestion-service"
"kafka"
"node-exporter"
```

### 3.3 Test Grafana Accessibility
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

**Expected Output:** `200`

## Step 4: Monitor Ingestion Service Logs

```bash
docker-compose logs -f ingestion
```

**Expected Output:**
```
ingestion_1  | 2024-01-XX XX:XX:XX,XXX - __main__ - INFO - Logging system initialized
ingestion_1  | 2024-01-XX XX:XX:XX,XXX - __main__ - INFO - Starting Air Quality Ingestion Service
ingestion_1  | 2024-01-XX XX:XX:XX,XXX - metrics - INFO - Metrics server started on port 8000
ingestion_1  | 2024-01-XX XX:XX:XX,XXX - __main__ - INFO - Metrics server started on port 8000
```

## Step 5: Access Monitoring Dashboards

### 5.1 Open Grafana Dashboard
1. Open browser and go to: http://localhost:3000
2. Login with:
   - Username: `admin`
   - Password: `admin`
3. Navigate to "Dashboards" → "Air Quality Ingestion Dashboard"

### 5.2 Open Prometheus
1. Go to: http://localhost:9090
2. Click on "Status" → "Targets" to verify all targets are UP
3. Go to "Graph" and try queries like:
   - `api_calls_total`
   - `rate(api_calls_total[5m])`
   - `validation_errors_total`

### 5.3 Open Kafka UI
1. Go to: http://localhost:8081
2. Check topics and message flow

## Step 6: Test Metrics Collection

### 6.1 Check API Call Metrics
```bash
curl -s http://localhost:8000/metrics | grep api_calls_total
```

### 6.2 Check Error Metrics
```bash
curl -s http://localhost:8000/metrics | grep errors_total
```

### 6.3 Check Processing Metrics
```bash
curl -s http://localhost:8000/metrics | grep processing_duration_seconds
```

## Step 7: Test Dead Letter Handling

### 7.1 Simulate Validation Error
The ingestion service will automatically handle validation errors. Monitor logs:

```bash
docker-compose logs -f ingestion | grep -i "dead letter\|validation"
```

### 7.2 Check Dead Letter Metrics
```bash
curl -s http://localhost:8000/metrics | grep dead_letter_messages_total
```

## Step 8: Test Log Aggregation

### 8.1 Check Loki Logs
```bash
curl -s "http://localhost:3100/loki/api/v1/query?query={job=\"containerlogs\"}" | jq '.data.result'
```

### 8.2 Test Log Search in Grafana
1. Go to Grafana → "Explore"
2. Select "Loki" as data source
3. Use query: `{container_name="capstone_ingestion_1"}`
4. Click "Run Query"

## Step 9: Test Error Classification

### 9.1 Monitor Different Error Types
```bash
# Watch for different error classifications
docker-compose logs -f ingestion | grep -E "(ERROR|WARNING)" | head -10
```

### 9.2 Check Error Metrics by Type
```bash
curl -s http://localhost:8000/metrics | grep "errors_total{" | head -5
```

## Step 10: Performance Testing

### 10.1 Monitor Processing Times
```bash
curl -s http://localhost:8000/metrics | grep processing_duration_seconds
```

### 10.2 Check Batch Processing Metrics
```bash
curl -s http://localhost:8000/metrics | grep batch_size
```

## Step 11: Verify Kafka Integration

### 11.1 Check Kafka Metrics
```bash
curl -s http://localhost:9308/metrics | grep kafka
```

### 11.2 Monitor Kafka Lag
```bash
curl -s http://localhost:8000/metrics | grep kafka_consumer_lag
```

## Step 12: Test Alerting (Optional)

### 12.1 Check Prometheus Rules
```bash
curl -s http://localhost:9090/api/v1/rules
```

### 12.2 Monitor High Error Rates
```bash
# Query for high error rates
curl -s "http://localhost:9090/api/v1/query?query=rate(errors_total[5m])" | jq
```

## Troubleshooting Common Issues

### Issue 1: Services Not Starting
```bash
# Check service status
docker-compose ps

# Check logs for specific service
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]
```

### Issue 2: Metrics Not Appearing
```bash
# Check if ingestion service is healthy
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### Issue 3: Grafana Not Loading Dashboards
```bash
# Check Grafana logs
docker-compose logs grafana

# Restart Grafana
docker-compose restart grafana
```

### Issue 4: Logs Not Appearing in Loki
```bash
# Check Promtail logs
docker-compose logs promtail

# Check Loki logs
docker-compose logs loki
```

## Expected Results Summary

After completing all tests, you should see:

1. ✅ All services running and healthy
2. ✅ Metrics being collected and exposed on port 8000
3. ✅ Prometheus scraping metrics successfully
4. ✅ Grafana dashboard showing real-time data
5. ✅ Structured logs with error classification
6. ✅ Dead letter message handling
7. ✅ Kafka metrics and lag monitoring
8. ✅ Log aggregation in Loki

## Cleanup

To stop all services:
```bash
docker-compose down
```

To remove all data volumes:
```bash
docker-compose down -v
```
