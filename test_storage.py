#!/usr/bin/env python3

import json
import time
from confluent_kafka import Producer
from datetime import datetime

# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092'
}

# Create producer
producer = Producer(kafka_config)

# Create a test message
test_message = {
    "city": "TestCity",
    "timestamp": int(datetime.now().timestamp() * 1000),  # Current time in milliseconds
    "pm2_5": 25.5,
    "pm10": 30.2,
    "ozone": 0.05,
    "carbon_monoxide": 1.2,
    "nitrogen_dioxide": 15.8,
    "sulphur_dioxide": 3.1,
    "uv_index": 6.5,
    "source": "test",
    "ingest_time": int(datetime.now().timestamp() * 1000)
}

# Send the message
producer.produce('air_quality_events', key='test_key', value=json.dumps(test_message))
producer.flush()

print(f"Sent test message: {test_message}")
