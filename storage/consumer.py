from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from repository import insert_air_quality_record
from config import KAFKA_BOOTSTRAP_SERVERS, SCHEMA_REGISTRY_URL, KAFKA_TOPIC, KAFKA_CONSUMER_GROUP
from logger import get_logger

logger = get_logger()

schema_registry_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
avro_deserializer = AvroDeserializer(schema_registry_client)

consumer_conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': KAFKA_CONSUMER_GROUP,
    'auto.offset.reset': 'earliest',
    'key.deserializer': lambda k, ctx: k.decode('utf-8'),
    'value.deserializer': avro_deserializer,
}

consumer = DeserializingConsumer(consumer_conf)
consumer.subscribe([KAFKA_TOPIC])

def consume_loop():
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka consumer error: {msg.error()}")
                continue

            record = msg.value()
            try:
                insert_air_quality_record(record)
                logger.info(f"Inserted record for city {record['city']} at {record['timestamp']}")
            except Exception as e:
                logger.error(f"Failed to insert record: {e}")
    except KeyboardInterrupt:
        logger.info("Shutdown requested, exiting...")
    finally:
        consumer.close()
