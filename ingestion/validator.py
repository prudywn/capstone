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

def validate_pollutant_value(field, value):
    if value is None:
        return False
    min_val, max_val = FIELD_RANGES.get(field, (None, None))
    if min_val is not None and max_val is not None:
        return min_val <= value <= max_val
    return True
