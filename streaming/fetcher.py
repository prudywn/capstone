import json
import logging
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from pymongo import MongoClient
import time

# Configurations
mongodb_uri = "mongodb://mongo:27017"
db_name = "air_quality"
collection_name = "curated_air_quality"
kafka_bootstrap_servers = "kafka:9092"
schema_registry_url = "http://schema-registry:8081"
kafka_topic = "air_quality_events"

# Load Avro schema string
with open("air_quality_event.avsc", "r") as f:
    avro_schema_str = f.read()

# Set up Schema Registry client and Avro serializer
schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
avro_serializer = AvroSerializer(schema_registry_client, avro_schema_str)

# Key serializer for Kafka (simple string serializer here)
def key_serializer(key, ctx):
    return key.encode('utf-8')

# Kafka producer setup with serializers
producer_conf = {
    "bootstrap.servers": kafka_bootstrap_servers,
    "key.serializer": key_serializer,
    "value.serializer": avro_serializer,
}

producer = SerializingProducer(producer_conf)

# MongoDB and collection
client = MongoClient(mongodb_uri)
collection = client[db_name][collection_name]

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def stream_mongo_changes():
    with collection.watch(full_document="updateLookup") as stream:
        for change in stream:
            try:
                full_doc = change["fullDocument"]
                # Parse timestamp string to datetime
                from datetime import datetime
                timestamp_str = full_doc["timestamp"]
                timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                timestamp_ms = int(timestamp_dt.timestamp() * 1000)
                
                # Prepare Kafka message key and value
                key = f"{full_doc['city']}_{timestamp_str}"
                value = {
                    "city": full_doc["city"],
                    "timestamp": timestamp_ms,
                    "pm2_5": full_doc.get("value") if full_doc.get("pollutant") == "pm2_5" else None,
                    "pm10": full_doc.get("value") if full_doc.get("pollutant") == "pm10" else None,
                    "ozone": full_doc.get("value") if full_doc.get("pollutant") == "ozone" else None,
                    "carbon_monoxide": full_doc.get("value") if full_doc.get("pollutant") == "carbon_monoxide" else None,
                    "nitrogen_dioxide": full_doc.get("value") if full_doc.get("pollutant") == "nitrogen_dioxide" else None,
                    "sulphur_dioxide": full_doc.get("value") if full_doc.get("pollutant") == "sulphur_dioxide" else None,
                    "uv_index": full_doc.get("value") if full_doc.get("pollutant") == "uv_index" else None,
                    "source": full_doc.get("source", "open-meteo"),
                    "ingest_time": timestamp_ms,
                }
                producer.produce(topic=kafka_topic, key=key, value=value, on_delivery=delivery_report)
                producer.poll(0)
            except Exception as e:
                logging.error(f"Error processing change event: {e}")
                time.sleep(1)

def flush_and_close():
    producer.flush()
