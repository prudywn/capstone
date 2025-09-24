from pymongo import MongoClient, UpdateOne
from config import MONGODB_URI, DB_NAME, RAW_CCOLLECTION, CURATED_COLLECTION
import logging
from metrics import MONGO_OPS

logger = logging.getLogger(__name__)

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
raw_col = db[RAW_CCOLLECTION]
curated_col = db[CURATED_COLLECTION]

def save_raw(city, raw_data):
    try:
        doc = {
            "city": city,
            "raw_payload": raw_data,
            "ingest_ts": raw_data.get("current_weather", {}).get("time"),
        }
        raw_col.insert_one(doc)
        MONGO_OPS.labels(operation="insert_raw", status="success").inc()
    except Exception as e:
        MONGO_OPS.labels(operation="insert_raw", status="fail").inc()
        logger.error(f"Error saving raw data for {city}: {e}")

def upsert_curated(city, records):
    # records is a list of dict with keys: timestamp, pollutant, value
    try:
        operations = []
        for rec in records:
            key = {
                "city": city,
                "timestamp": rec["timestamp"],
                "pollutant": rec["pollutant"],
            }
            doc = {
                "$set": {
                    "value": rec["value"],
                    "source": "open-meteo",
                }
            }
            operations.append(UpdateOne(key, doc, upsert=True))
        if operations:
            curated_col.bulk_write(operations)
        MONGO_OPS.labels(operation="upsert_curated", status="success").inc()
    except Exception as e:
        MONGO_OPS.labels(operation="upsert_curated", status="fail").inc()
        logger.error(f"Error upserting curated data for {city}: {e}")