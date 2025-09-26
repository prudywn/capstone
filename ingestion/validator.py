import logging
from metrics import record_validation_error, ERRORS

logger = logging.getLogger(__name__)

# Define safe ranges for pollutants
FIELD_RANGES = {
    "pm2_5": (0, 1000),  # example safe ranges
    "pm10": (0, 1000),
    "ozone": (0, 1000),
    "carbon_monoxide": (0, 10000),
    "nitrogen_dioxide": (0, 1000),
    "sulphur_dioxide": (0, 1000),
    "uv_index": (0, 20),
}

def validate_pollutant_value(field, value, city="unknown"):
    """Validate pollutant value and record metrics for invalid values"""
    if value is None:
        logger.debug(f"Null value for {field} in {city}")
        record_validation_error(city, field)
        return False
        
    if not isinstance(value, (int, float)):
        logger.warning(f"Invalid type for {field} in {city}: {type(value)}")
        record_validation_error(city, field)
        ERRORS.labels(error_type="validation_type", city=city).inc()
        return False
        
    min_val, max_val = FIELD_RANGES.get(field, (None, None))
    if min_val is not None and max_val is not None:
        if value < min_val:
            logger.warning(f"Value below minimum for {field} in {city}: {value} < {min_val}")
            record_validation_error(city, field)
            ERRORS.labels(error_type="validation_range", city=city).inc()
            return False
        elif value > max_val:
            logger.warning(f"Value above maximum for {field} in {city}: {value} > {max_val}")
            record_validation_error(city, field)
            ERRORS.labels(error_type="validation_range", city=city).inc()
            return False
            
    return True

def validate_data_quality(data, city):
    """Validate overall data quality and return quality score"""
    if not data:
        logger.error(f"Empty data received for {city}")
        ERRORS.labels(error_type="empty_data", city=city).inc()
        return False, 0.0
        
    hourly = data.get('hourly', {})
    if not hourly:
        logger.error(f"No hourly data for {city}")
        ERRORS.labels(error_type="missing_hourly", city=city).inc()
        return False, 0.0
        
    timestamps = hourly.get('time', [])
    if not timestamps:
        logger.error(f"No timestamps for {city}")
        ERRORS.labels(error_type="missing_timestamps", city=city).inc()
        return False, 0.0
        
    # Calculate data completeness
    pollutants = ["pm2_5", "pm10", "ozone", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "uv_index"]
    total_expected = len(timestamps) * len(pollutants)
    valid_count = 0
    
    for pollutant in pollutants:
        values = hourly.get(pollutant, [])
        for i, value in enumerate(values):
            if i < len(timestamps) and validate_pollutant_value(pollutant, value, city):
                valid_count += 1
                
    quality_score = valid_count / total_expected if total_expected > 0 else 0.0
    
    if quality_score < 0.5:
        logger.warning(f"Low data quality for {city}: {quality_score:.2%}")
        ERRORS.labels(error_type="low_quality", city=city).inc()
        
    logger.info(f"Data quality for {city}: {quality_score:.2%} ({valid_count}/{total_expected})")
    return quality_score > 0.5, quality_score
