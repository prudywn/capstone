# Grafana Dashboard Setup Guide

## Quick Access

1. **Open Grafana**: Go to http://localhost:3000
2. **Login**: 
   - Username: `admin`
   - Password: `admin`
3. **Access Dashboard**: The "Air Quality Ingestion Dashboard" should appear automatically

## If Dashboard Doesn't Appear

### Step 1: Check Data Sources
1. Go to **Configuration** → **Data Sources**
2. Verify **Prometheus** is configured and shows "Data source is working"
3. If not, click **Prometheus** and test the connection

### Step 2: Import Dashboard Manually
1. Go to **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Upload the file: `monitoring/grafana-dashboards/air-quality-dashboard.json`
4. Click **Import**

### Step 3: Verify Metrics
1. Go to **Explore** in the left menu
2. Select **Prometheus** as data source
3. Try these queries:
   - `api_calls_total`
   - `rate(api_calls_total[5m])`
   - `validation_errors_total`
   - `errors_total`

## Dashboard Panels

The dashboard includes:

1. **API Calls Rate**: Shows API call frequency by city and status
2. **Validation Errors**: Displays validation error counts
3. **MongoDB Operations**: Tracks database operation rates
4. **Kafka Lag**: Shows consumer lag (simulated)
5. **Error Rate**: Displays error rates by type

## Troubleshooting

### Dashboard Not Loading
```bash
# Check Grafana logs
docker-compose logs grafana

# Restart Grafana
docker-compose restart grafana
```

### No Data in Dashboard
```bash
# Check if metrics are being collected
curl http://localhost:8000/metrics | grep api_calls_total

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

### Data Source Issues
1. In Grafana, go to **Configuration** → **Data Sources**
2. Click **Prometheus**
3. Update URL to: `http://prometheus:9090`
4. Click **Save & Test**

## Expected Results

After successful setup, you should see:
- Real-time metrics updating every 5 seconds
- API call rates showing successful and failed calls
- Error counts for different error types
- Processing times and batch sizes
- MongoDB operation success/failure rates

## Next Steps

1. **Set up Alerts**: Configure alerts for high error rates
2. **Customize Dashboards**: Add more panels as needed
3. **Monitor Logs**: Use Loki integration for log analysis
4. **Scale Monitoring**: Add more services to monitoring
