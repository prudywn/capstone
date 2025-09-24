from cassandra_session import get_session
import datetime

session = get_session()

insert_stmt = session.prepare("""
    INSERT INTO air_quality_by_city_date (city, date, hour, pm2_5, pm10, ozone, carbon_monoxide,
                                         nitrogen_dioxide, sulphur_dioxide, uv_index, ingest_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

def insert_air_quality_record(record):
    ts = datetime.datetime.utcfromtimestamp(record['timestamp'] / 1000)
    date_str = ts.strftime('%Y-%m-%d')
    hour = ts.hour

    ingest_time = datetime.datetime.utcfromtimestamp(record['ingest_time'] / 1000) if record.get('ingest_time') else None

    session.execute(insert_stmt, (
        record['city'],
        date_str,
        hour,
        record.get('pm2_5'),
        record.get('pm10'),
        record.get('ozone'),
        record.get('carbon_monoxide'),
        record.get('nitrogen_dioxide'),
        record.get('sulphur_dioxide'),
        record.get('uv_index'),
        ingest_time
    ))
