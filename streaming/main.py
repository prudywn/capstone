import signal
import sys
import logging
from fetcher import stream_mongo_changes, flush_and_close

def signal_handler(sig, frame):
    logging.info("Shutdown signal received, cleaning up...")
    flush_and_close()
    sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        stream_mongo_changes()
    except Exception as e:
        logging.error(f"Fatal error in streaming: {e}")
        flush_and_close()
