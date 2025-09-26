from apscheduler.schedulers.blocking import BlockingScheduler
from fetcher import fetch_city_air_quality
from validator import validate_pollutant_value, validate_data_quality
from storage import save_raw, upsert_curated
from config import CITIES, BACKFILL_DAYS
from datetime import datetime, timedelta
from metrics import record_processing_time, record_records_processed, record_mongo_operation, ERRORS, BATCH_SIZE
from dead_letter_handler import DeadLetterHandler
import time
import logging

logger = logging.getLogger(__name__)
dead_letter_handler = DeadLetterHandler()

def process_city(city):
    """Process air quality data for a single city with comprehensive error handling"""
    start_time = time.time()
    logger.info(f"Starting processing for {city}")
    
    try:
        # Fetch data
        data = fetch_city_air_quality(city)
        
        # Validate data quality
        is_valid, quality_score = validate_data_quality(data, city)
        if not is_valid:
            logger.error(f"Data quality too low for {city}: {quality_score:.2%}")
            dead_letter_handler.handle_processing_error(data, city, "low_data_quality")
            return False
            
        # Save raw data
        try:
            save_raw(city, data)
            record_mongo_operation("save_raw", True)
            logger.info(f"Saved raw data for {city}")
        except Exception as e:
            logger.error(f"Failed to save raw data for {city}: {str(e)}")
            record_mongo_operation("save_raw", False)
            dead_letter_handler.handle_processing_error(data, city, "save_raw_failure")
            raise

        # Process and validate records
        hourly = data.get('hourly', {})
        timestamps = hourly.get('time', [])
        pollutants = ["pm2_5", "pm10", "ozone", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "uv_index"]
        
        records = []
        validation_errors = 0
        
        for i, ts in enumerate(timestamps):
            for p in pollutants:
                values = hourly.get(p, [])
                if i < len(values):
                    value = values[i]
                    if validate_pollutant_value(p, value, city):
                        records.append({"timestamp": ts, "pollutant": p, "value": value})
                    else:
                        validation_errors += 1

        # Record batch metrics
        BATCH_SIZE.labels(city=city).observe(len(records))
        record_records_processed(city, len(records), True)
        
        if validation_errors > 0:
            logger.warning(f"Validation errors for {city}: {validation_errors} invalid values")
            ERRORS.labels(error_type="validation_batch", city=city).inc()

        # Save curated data
        try:
            upsert_curated(city, records)
            record_mongo_operation("upsert_curated", True)
            logger.info(f"Saved {len(records)} curated records for {city}")
        except Exception as e:
            logger.error(f"Failed to save curated data for {city}: {str(e)}")
            record_mongo_operation("upsert_curated", False)
            dead_letter_handler.handle_processing_error(data, city, "upsert_curated_failure")
            raise

        # Record processing time
        duration = time.time() - start_time
        record_processing_time(city, "full_processing", duration)
        logger.info(f"Successfully processed {city} in {duration:.2f}s")
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed to process {city} after {duration:.2f}s: {str(e)}")
        ERRORS.labels(error_type="processing_failure", city=city).inc()
        record_processing_time(city, "failed_processing", duration)
        dead_letter_handler.handle_processing_error({"city": city, "error": str(e)}, city, "processing_failure")
        return False

def scheduled_job():
    """Scheduled job to process all cities"""
    logger.info("Starting scheduled processing job")
    start_time = time.time()
    
    success_count = 0
    failure_count = 0
    
    for city in CITIES.keys():
        try:
            success = process_city(city)
            if success:
                success_count += 1
                logger.info(f"Successfully processed {city}")
            else:
                failure_count += 1
                logger.error(f"Failed to process {city}")
        except Exception as e:
            failure_count += 1
            logger.error(f"Exception processing {city}: {str(e)}")
            ERRORS.labels(error_type="scheduled_job_error", city=city).inc()
    
    duration = time.time() - start_time
    logger.info(f"Scheduled job completed in {duration:.2f}s: {success_count} success, {failure_count} failures")
    
    # Record job-level metrics
    if failure_count > 0:
        ERRORS.labels(error_type="scheduled_job_failures", city="all").inc(failure_count)

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
