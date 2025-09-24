from consumer import consume_loop
from logger import get_logger

logger = get_logger()

if __name__ == "__main__":
    logger.info("Starting storage service Kafka consumer...")
    consume_loop()
