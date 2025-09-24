import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "air_quality_events")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "storage_service_group")

CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", "cassandra").split(",")
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "air_quality_keyspace")
