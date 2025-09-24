import requests
from config import API_TEMPLATE, CITIES
from metrics import API_CALLS

def fetch_city_air_quality(city_name, start_date=None, end_date=None):
    loc = CITIES.get(city_name)

    if not loc:
        raise ValueError(f'Unknown city {city_name}')

    try:
        base_url = API_TEMPLATE.format(loc['lat'], loc['lon'])
        url = base_url
        if start_date and end_date:
            url += f"&start_date={start_date}&end_date={end_date}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        API_CALLS.labels(city=city_name, status="success").inc()
        return response.json()
    except Exception as e:
        API_CALLS.labels(city=city_name, status="fail").inc()
        raise e