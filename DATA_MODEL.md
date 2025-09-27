# Air Quality Data Pipeline - Data Model & Retention Plan

## Data Model Overview

The air quality data pipeline uses a hybrid storage approach with two primary data stores optimized for different access patterns:

- **MongoDB**: Raw data storage for audit trails and debugging
- **Cassandra**: Processed time-series data for analytics and queries

## Data Flow Architecture

```
[External API]
      ↓ Fetch raw data
┌───────────────┐
│ MongoDB       │  ← Stores raw JSON documents (audit trail)
│  (Raw Data)   │
└───────────────┘
      ↓ Validate & Curate Data
      ↓
┌───────────────┐          ┌───────────────┐
│ Kafka         │  ← Streams validated events   │ Cassandra
│ (Distributed  │  --------------------------→  │ (Time-series DB)
│  Event Stream)│                              │ (Curated data for analytics)
└───────────────┘          └───────────────┘


```

## MongoDB Data Model (Raw Storage)

### Database: `air_quality`
### Collections: `raw_air_quality`, `curated_air_quality`

#### Raw Air Quality Collection (`raw_air_quality`)

**Purpose**: Store original API responses for audit trails and debugging

```javascript
{
  "_id": ObjectId,
  "city": "Nairobi" | "Mombasa",
  "raw_payload": {
    "current_weather": {
      "time": "2024-01-15T12:00",
      "temperature_2m": 25.5,
      "relative_humidity_2m": 65,
      "apparent_temperature": 27.2,
      "is_day": 1,
      "precipitation": 0.0,
      "rain": 0.0,
      "showers": 0.0,
      "snowfall": 0.0,
      "weather_code": 1,
      "cloud_cover": 25,
      "pressure_msl": 1013.2,
      "surface_pressure": 1008.5,
      "wind_speed_10m": 3.2,
      "wind_direction_10m": 180
    },
    "hourly": {
      "time": ["2024-01-15T00:00", "2024-01-15T01:00", ...],
      "pm2_5": [15.2, 18.5, 12.3, ...],
      "pm10": [25.8, 30.1, 22.4, ...],
      "ozone": [45.2, 48.7, 42.1, ...],
      "carbon_monoxide": [0.8, 0.9, 0.7, ...],
      "nitrogen_dioxide": [12.5, 15.2, 10.8, ...],
      "sulphur_dioxide": [2.1, 2.5, 1.8, ...],
      "uv_index": [8.5, 0.0, 0.0, ...]
    }
  },
  "ingest_ts": "2024-01-15T12:00:00Z",
  "created_at": ISODate("2024-01-15T12:00:00Z")
}
```

#### Curated Air Quality Collection (`curated_air_quality`)

**Purpose**: Store processed and validated individual records

```javascript
{
  "_id": ObjectId,
  "city": "Nairobi" | "Mombasa",
  "timestamp": ISODate("2024-01-15T12:00:00Z"),
  "pollutant": "pm2_5" | "pm10" | "ozone" | "carbon_monoxide" | "nitrogen_dioxide" | "sulphur_dioxide" | "uv_index",
  "value": 15.2,
  "quality_score": 0.95,
  "validation_status": "valid" | "invalid" | "warning",
  "source": "open-meteo",
  "ingest_time": ISODate("2024-01-15T12:00:00Z"),
  "created_at": ISODate("2024-01-15T12:00:00Z")
}
```

## Cassandra Data Model (Processed Storage)

### Keyspace: `air_quality_keyspace`
### Table: `air_quality_by_city_date`

**Purpose**: Optimized time-series storage for analytics and queries

```sql
CREATE TABLE air_quality_by_city_date (
    city text,
    date text,
    hour int,
    pm2_5 float,
    pm10 float,
    ozone float,
    carbon_monoxide float,
    nitrogen_dioxide float,
    sulphur_dioxide float,
    uv_index float,
    ingest_time timestamp,
    PRIMARY KEY ((city, date), hour)
) WITH CLUSTERING ORDER BY (hour DESC);
```

#### Schema Details

- **Partition Key**: `(city, date)` - Enables efficient queries by city and date
- **Clustering Key**: `hour DESC` - Orders data by hour (newest first)
- **Data Types**:
  - `city`: Text (Nairobi, Mombasa)
  - `date`: Text (YYYY-MM-DD format)
  - `hour`: Integer (0-23)
  - `pollutants`: Float (nullable for missing values)
  - `ingest_time`: Timestamp (when data was processed)

#### Sample Record

```sql
INSERT INTO air_quality_by_city_date 
(city, date, hour, pm2_5, pm10, ozone, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, uv_index, ingest_time)
VALUES 
('Nairobi', '2024-01-15', 12, 15.2, 25.8, 45.2, 0.8, 12.5, 2.1, 8.5, '2024-01-15T12:00:00Z');
```

## Kafka Event Schema (Avro)

### Topic: `air_quality_events`
### Schema: `AirQualityEvent`

```json
{
  "namespace": "com.airquality",
  "type": "record",
  "name": "AirQualityEvent",
  "version": "1",
  "fields": [
    {"name": "city", "type": "string"},
    {"name": "timestamp", "type": {
      "type": "long",
      "logicalType": "timestamp-millis"
    }},
    {"name": "pm2_5", "type": ["null", "float"], "default": null},
    {"name": "pm10", "type": ["null", "float"], "default": null},
    {"name": "ozone", "type": ["null", "float"], "default": null},
    {"name": "carbon_monoxide", "type": ["null", "float"], "default": null},
    {"name": "nitrogen_dioxide", "type": ["null", "float"], "default": null},
    {"name": "sulphur_dioxide", "type": ["null", "float"], "default": null},
    {"name": "uv_index", "type": ["null", "float"], "default": null},
    {"name": "source", "type": "string"},
    {"name": "ingest_time", "type": {
      "type": "long",
      "logicalType": "timestamp-millis"
    }}
  ]
}
```

## Data Validation Rules

### Pollutant Value Ranges

| Pollutant | Valid Range | Unit | Notes |
|-----------|-------------|------|-------|
| **PM2.5** | 0 - 500 | μg/m³ | WHO guideline: 15 μg/m³ (24h avg) |
| **PM10** | 0 - 600 | μg/m³ | WHO guideline: 45 μg/m³ (24h avg) |
| **Ozone** | 0 - 500 | μg/m³ | WHO guideline: 100 μg/m³ (8h avg) |
| **CO** | 0 - 50 | mg/m³ | WHO guideline: 4 mg/m³ (24h avg) |
| **NO₂** | 0 - 400 | μg/m³ | WHO guideline: 25 μg/m³ (24h avg) |
| **SO₂** | 0 - 1000 | μg/m³ | WHO guideline: 40 μg/m³ (24h avg) |
| **UV Index** | 0 - 20 | Index | WHO scale: 0-11+ |

### Data Quality Metrics

- **Completeness**: Minimum 80% of expected pollutants present
- **Consistency**: Values within expected ranges
- **Timeliness**: Data ingested within 2 hours of collection
- **Accuracy**: Cross-validation with historical patterns

## Data Retention Plan

### MongoDB Retention Policy

#### Raw Data Collection (`raw_air_quality`)
- **Retention Period**: 90 days
- **Cleanup Strategy**: Automated TTL index
- **Purpose**: Debugging and audit trails

```javascript
// TTL Index for automatic cleanup
db.raw_air_quality.createIndex(
  { "ingest_ts": 1 },
  { expireAfterSeconds: 7776000 } // 90 days
)
```

#### Curated Data Collection (`curated_air_quality`)
- **Retention Period**: 1 year
- **Cleanup Strategy**: Monthly batch cleanup
- **Purpose**: Detailed analysis and validation

```javascript
// Monthly cleanup script
db.curated_air_quality.deleteMany({
  "created_at": { $lt: new Date(Date.now() - 365*24*60*60*1000) }
})
```

### Cassandra Retention Policy

#### Processed Data Table (`air_quality_by_city_date`)
- **Retention Period**: 2 years
- **Cleanup Strategy**: TTL on individual records
- **Purpose**: Analytics and reporting

```sql
-- TTL for individual records (2 years = 63072000 seconds)
INSERT INTO air_quality_by_city_date 
(city, date, hour, pm2_5, ...) 
VALUES 
('Nairobi', '2024-01-15', 12, 15.2, ...) 
USING TTL 63072000;
```

### Kafka Topic Retention

#### Main Topic (`air_quality_events`)
- **Retention Period**: 7 days
- **Segment Size**: 1GB
- **Cleanup Policy**: `delete`

#### Dead Letter Topic (`air_quality_events_dlq`)
- **Retention Period**: 30 days
- **Segment Size**: 100MB
- **Cleanup Policy**: `delete`

## Data Archival Strategy

### Long-term Storage

1. **Monthly Archives**
   - Export processed data to Parquet files
   - Store in cloud storage (S3/GCS)
   - Compress with gzip for efficiency

2. **Aggregated Data**
   - Daily averages by city
   - Monthly summaries
   - Annual trends

### Archive Format

```json
{
  "city": "Nairobi",
  "date": "2024-01-15",
  "daily_averages": {
    "pm2_5": 18.5,
    "pm10": 28.2,
    "ozone": 45.8,
    "carbon_monoxide": 0.9,
    "nitrogen_dioxide": 14.2,
    "sulphur_dioxide": 2.3,
    "uv_index": 6.8
  },
  "max_values": { ... },
  "min_values": { ... },
  "data_quality_score": 0.92,
  "record_count": 24
}
```

## Data Governance

### Access Control

- **Read Access**: Analytics team, researchers
- **Write Access**: Ingestion service only
- **Admin Access**: DevOps team, data engineers

### Data Lineage

1. **Source**: Open-Meteo API
2. **Ingestion**: Python service with validation
3. **Storage**: MongoDB → Kafka → Cassandra
4. **Monitoring**: Prometheus metrics and Grafana dashboards

### Compliance

- **Data Privacy**: No personal information collected
- **Data Quality**: Automated validation and monitoring
- **Audit Trail**: Complete data lineage tracking
- **Retention**: Automated cleanup per retention policies

## Performance Optimization

### MongoDB Indexes

```javascript
// City and timestamp index for queries
db.raw_air_quality.createIndex({ "city": 1, "ingest_ts": -1 })

// TTL index for automatic cleanup
db.raw_air_quality.createIndex({ "ingest_ts": 1 }, { expireAfterSeconds: 7776000 })
```

### Cassandra Optimization

- **Partitioning**: By city and date for efficient queries
- **Clustering**: By hour (DESC) for time-series access
- **Compression**: LZ4Compressor for storage efficiency
- **Caching**: Row cache for frequently accessed data

### Query Patterns

#### Common Queries

1. **Latest data by city**
   ```sql
   SELECT * FROM air_quality_by_city_date 
   WHERE city = 'Nairobi' AND date = '2025-09-25' 
   ORDER BY hour DESC LIMIT 1;
   ```

2. **Daily averages**
   ```sql
   SELECT city, date, 
          AVG(pm2_5) as avg_pm2_5,
          AVG(pm10) as avg_pm10
   FROM air_quality_by_city_date 
   WHERE city = 'Nairobi' AND date >= '2025-09-24'
   GROUP BY city, date;
   ```

3. **Hourly trends**
   ```sql
   SELECT hour, pm2_5, pm10 
   FROM air_quality_by_city_date 
   WHERE city = 'Nairobi' AND date = '2024-01-15'
   ORDER BY hour;
   ```
