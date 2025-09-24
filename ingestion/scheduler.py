from apscheduler.schedulers.blocking import BlockingScheduler
from fetcher import fetch_city_air_quality
from validator import validate_pollutant_value
from storage import save_raw, upsert_curated
from config import CITIES, BACKFILL_DAYS
from datetime import datetime, timedelta

def process_city(city):
    data = fetch_city_air_quality(city)
    save_raw(city, data)

    hourly = data.get('hourly', {})
    timestamps = hourly.get('time', [])
    pollutants = ["pm2_5", "pm10", "ozone", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "uv_index"]
    
    records = []
    for i, ts in enumerate(timestamps):
        for p in pollutants:
            values = hourly.get(p, [])
            if i < len(values):
                value = values[i]
                if validate_pollutant_value(p, value):
                    records.append({"timestamp": ts, "pollutant": p, "value": value})

    upsert_curated(city, records)

def scheduled_job():
    for city in CITIES.keys():
        try:
            process_city(city)
            print(f"Processed {city}")
        except Exception as e:
            print(f"Error processing {city}: {e}")

def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_job, 'interval', seconds=3600)  # hourly
    scheduler.start()

def run_backfill():
    try:
        today = datetime.utcnow().date()
        for delta in range(BACKFILL_DAYS, 0, -1):
            day = today - timedelta(days=delta)
            day_str = day.isoformat()
            for city in CITIES.keys():
                try:
                    print(f"Backfilling {city} for {day_str}")
                    data = fetch_city_air_quality(city, start_date=day_str, end_date=day_str)
                    save_raw(city, data)

                    # Process hourly data
                    hourly = data.get("hourly", {})
                    timestamps = hourly.get("time", [])
                    pollutants = ["pm2_5", "pm10", "ozone", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "uv_index"]

                    records = []
                    for i, ts in enumerate(timestamps):
                        for p in pollutants:
                            values = hourly.get(p, [])
                            if i < len(values):
                                value = values[i]
                                if validate_pollutant_value(p, value):
                                    records.append({"timestamp": ts, "pollutant": p, "value": value})
                    upsert_curated(city, records)
                except Exception as ex:
                    print(f"Backfill error for {city} on {day_str}: {ex}")
    except Exception as ex:
        print(f"Backfill setup failed: {ex}")
