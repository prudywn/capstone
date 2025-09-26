import os
from datetime import datetime, timedelta

# API endpoint with placeholders for lat/lon
API_TEMPLATE = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude={}&longitude={}&hourly=pm2_5,pm10,ozone,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,uv_index&timezone=Africa/Nairobi"

CITIES = {
    "Nairobi": {"lat": -1.286389, "lon": 36.817223},
    "Mombasa": {"lat": -4.043477, "lon": 39.668206},
}

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "air_quality")
RAW_CCOLLECTION = "raw_air_quality"
CURATED_COLLECTION = "curated_air_quality"

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 3600))  # hourly
BACKFILL_DAYS = int(os.getenv("BACKFILL_DAYS", 5))