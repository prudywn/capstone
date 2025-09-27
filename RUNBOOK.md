# Air Quality Data Pipeline - Runbook

## Local Setup Guide

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 27017, 8000, 8080, 8081, 9042, 9090, 9092, 3000 available
- Terminal/Command line access

### Quick Start

1. **Clone and Navigate**
   ```bash
   cd /home/prudy/capstone
   ```

2. **Start All Services**
   ```bash
   docker-compose up -d
   ```

3. **Verify Services**
   ```bash
   docker-compose ps
   ```

4. **Check Logs**
   ```bash
   docker-compose logs -f ingestion
   ```

### Service Health Checks

| Service | Health Check | Expected Response |
|---------|-------------|-------------------|
| **MongoDB** | `docker exec mongo mongosh --eval "db.runCommand('ping')"` | `{ ok: 1 }` |
| **Kafka** | `docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list` | List of topics |
| **Cassandra** | `docker exec cassandra cqlsh -e "SELECT release_version FROM system.local"` | Version info |
| **Ingestion** | `curl http://localhost:8000/metrics` | Prometheus metrics |
| **Prometheus** | `curl http://localhost:9090/api/v1/targets` | Target status |
| **Grafana** | `curl http://localhost:3000/api/health` | `{"database":"ok"}` |

## Environment Variables

### Ingestion Service

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://mongo:27017/air_quality` | MongoDB connection string |
| `POLL_INTERVAL_SECONDS` | `3600` | Data collection frequency (seconds) |
| `BACKFILL_DAYS` | `5` | Days of historical data to backfill |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARN, ERROR) |

### Storage Service

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Kafka broker addresses |
| `SCHEMA_REGISTRY_URL` | `http://schema-registry:8081` | Schema registry endpoint |
| `KAFKA_TOPIC` | `air_quality_events` | Kafka topic name |
| `KAFKA_CONSUMER_GROUP` | `storage_service_group` | Consumer group ID |
| `CASSANDRA_HOSTS` | `cassandra` | Cassandra node addresses |
| `CASSANDRA_KEYSPACE` | `air_quality_keyspace` | Cassandra keyspace name |

### Streaming Service

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://mongo:27017/air_quality` | MongoDB connection string |
| `KAFKA_BROKER` | `kafka:9092` | Kafka broker address |
| `KAFKA_TOPIC` | `air_quality_events` | Kafka topic name |
| `SCHEMA_REGISTRY_URL` | `http://schema-registry:8081` | Schema registry endpoint |

## Backfill Commands

### Manual Backfill

1. **Single City Backfill**
   ```bash
   docker exec air_quality_ingestion python -c "
   from scheduler import run_backfill
   run_backfill()
   "
   ```

2. **Custom Backfill Period**
   ```bash
   # Set custom backfill days
   docker-compose exec ingestion bash -c "
   export BACKFILL_DAYS=10
   python -c 'from scheduler import run_backfill; run_backfill()'
   "
   ```

3. **Specific Date Range**
   ```bash
   docker exec air_quality_ingestion python -c "
   from fetcher import fetch_city_air_quality
   from storage import save_raw, upsert_curated
   from datetime import datetime, timedelta
   
   # Backfill specific date range
   start_date = '2024-01-01'
   end_date = '2024-01-07'
   
   for city in ['Nairobi', 'Mombasa']:
       data = fetch_city_air_quality(city, start_date=start_date, end_date=end_date)
       save_raw(city, data)
       # Process and save curated data...
   "
   ```

### Automated Backfill

The ingestion service automatically runs backfill on startup:

```bash
# View backfill logs
docker-compose logs ingestion | grep -i backfill

# Check backfill progress
docker exec air_quality_ingestion python -c "
from config import BACKFILL_DAYS
print(f'Backfilling {BACKFILL_DAYS} days of data')
"
```

## Data Validation Commands

### Check Data Quality

1. **MongoDB Raw Data**
   ```bash
   docker exec mongo mongosh air_quality --eval "
   db.raw_air_quality.countDocuments()
   db.raw_air_quality.aggregate([
     { \$group: { _id: '\$city', count: { \$sum: 1 } } }
   ])
   "
   ```

2. **Cassandra Processed Data**
   ```bash
   docker exec cassandra cqlsh -e "
   USE air_quality_keyspace;
   SELECT city, date, COUNT(*) as records 
   FROM air_quality_by_city_date 
   GROUP BY city, date 
   ORDER BY city, date DESC 
   LIMIT 10;
   "
   ```

3. **Kafka Topic Status**
   ```bash
   docker exec kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic air_quality_events \
     --from-beginning \
     --max-messages 5
   ```

## Monitoring Commands

### Metrics

1. **Prometheus Metrics**
   ```bash
   # Check ingestion metrics
   curl http://localhost:8000/metrics | grep api_calls_total
   
   # Check Prometheus targets
   curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health == "up")'
   ```

2. **Grafana Dashboard**
   - URL: http://localhost:3000
   - Login: admin/admin
   - Dashboard: "Air Quality Ingestion Dashboard"

### Logs

1. **Service Logs**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f ingestion
   docker-compose logs -f storage
   docker-compose logs -f streaming
   ```

2. **Loki Logs**
   ```bash
   # Query logs via Loki API
   curl -G "http://localhost:3100/loki/api/v1/query" \
     --data-urlencode 'query={job="ingestion"}' \
     --data-urlencode 'limit=10'
   ```

## Troubleshooting

### Common Issues

1. **Services Not Starting**
   ```bash
   # Check Docker resources
   docker system df
   docker system prune -f
   
   # Restart services
   docker-compose down
   docker-compose up -d
   ```

2. **Database Connection Issues**
   ```bash
   # MongoDB
   docker exec mongo mongosh --eval "db.runCommand('ping')"
   
   # Cassandra
   docker exec cassandra cqlsh -e "SELECT release_version FROM system.local"
   ```

3. **Kafka Issues**
   ```bash
   # Check Kafka topics
   docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
   
   # Check consumer groups
   docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list
   ```

4. **Data Not Flowing**
   ```bash
   # Check ingestion service
   docker-compose logs ingestion | tail -20
   
   # Check metrics
   curl http://localhost:8000/metrics | grep -E "(api_calls_total|errors_total)"
   
   # Check Kafka messages
   docker exec kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic air_quality_events \
     --from-beginning \
     --max-messages 1
   ```

### Performance Tuning

1. **Increase Polling Frequency**
   ```bash
   # Update environment variable
   docker-compose exec ingestion bash -c "
   export POLL_INTERVAL_SECONDS=1800  # 30 minutes
   python -c 'from scheduler import start_scheduler; start_scheduler()'
   "
   ```

2. **Adjust Batch Sizes**
   ```bash
   # Check current batch size
   curl http://localhost:8000/metrics | grep batch_size
   ```

3. **Monitor Resource Usage**
   ```bash
   # Container resource usage
   docker stats
   
   # Disk usage
   docker system df
   ```

## Maintenance

### Regular Tasks

1. **Log Rotation**
   - Logs are automatically rotated (max 10MB, 3 files)
   - Manual cleanup: `docker-compose logs --tail=0 -f`

2. **Data Cleanup**
   ```bash
   # MongoDB cleanup (if needed)
   docker exec mongo mongosh air_quality --eval "
   db.raw_air_quality.deleteMany({
     ingest_ts: { \$lt: new Date(Date.now() - 30*24*60*60*1000) }
   })
   "
   ```

3. **Health Monitoring**
   ```bash
   # Daily health check script
   #!/bin/bash
   curl -f http://localhost:8000/metrics > /dev/null && echo "Ingestion OK" || echo "Ingestion FAILED"
   curl -f http://localhost:9090/api/v1/targets > /dev/null && echo "Prometheus OK" || echo "Prometheus FAILED"
   curl -f http://localhost:3000/api/health > /dev/null && echo "Grafana OK" || echo "Grafana FAILED"
   ```

### Backup Procedures

1. **MongoDB Backup**
   ```bash
   docker exec mongo mongodump --db air_quality --out /backup
   docker cp mongo:/backup ./mongodb_backup
   ```

2. **Cassandra Backup**
   ```bash
   docker exec cassandra nodetool snapshot air_quality_keyspace
   ```

3. **Configuration Backup**
   ```bash
   # Backup Docker Compose and configs
   tar -czf config_backup.tar.gz docker-compose.yml monitoring/ ingestion/ streaming/ storage/
   ```
