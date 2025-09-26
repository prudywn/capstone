import requests
import time
import logging
from config import API_TEMPLATE, CITIES
from metrics import record_api_call, record_processing_time, ERRORS

logger = logging.getLogger(__name__)

def fetch_city_air_quality(city_name, start_date=None, end_date=None):
    loc = CITIES.get(city_name)

    if not loc:
        logger.error(f"Unknown city: {city_name}")
        ERRORS.labels(error_type="config", city=city_name).inc()
        raise ValueError(f'Unknown city {city_name}')

    start_time = time.time()
    
    try:
        base_url = API_TEMPLATE.format(loc['lat'], loc['lon'])
        url = base_url
        if start_date and end_date:
            url += f"&start_date={start_date}&end_date={end_date}"
        
        logger.info(f"Fetching air quality data for {city_name}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        duration = time.time() - start_time
        record_api_call(city_name, True, duration)
        record_processing_time(city_name, "api_fetch", duration)
        
        logger.info(f"Successfully fetched data for {city_name} in {duration:.2f}s")
        return response.json()
        
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        logger.error(f"API timeout for {city_name} after {duration:.2f}s")
        record_api_call(city_name, False, duration)
        ERRORS.labels(error_type="api_timeout", city=city_name).inc()
        raise
        
    except requests.exceptions.RequestException as e:
        duration = time.time() - start_time
        logger.error(f"API request failed for {city_name}: {str(e)}")
        record_api_call(city_name, False, duration)
        ERRORS.labels(error_type="api_error", city=city_name).inc()
        raise
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Unexpected error fetching data for {city_name}: {str(e)}")
        record_api_call(city_name, False, duration)
        ERRORS.labels(error_type="unexpected", city=city_name).inc()
        raise