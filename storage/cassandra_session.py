import time
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from config import CASSANDRA_HOSTS, CASSANDRA_KEYSPACE
from logger import get_logger

logger = get_logger()


def create_keyspace(session):
    query = f"""
    CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE} WITH replication = {{
        'class': 'SimpleStrategy',
        'replication_factor': '1'
    }};
    """
    session.execute(query)
    logger.info(f"Ensured keyspace {CASSANDRA_KEYSPACE} exists.")


def create_table(session):
    query = f"""
    CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.air_quality_by_city_date (
        city text,
        date text,
        hour int,
        pm2_5 float,
        pm10 float,
        ozone float,
        carbon_monoxide float,
        nitrogen_dioxide float,
        sulphur_dioxide float,
        uv_index float,
        ingest_time timestamp,
        PRIMARY KEY ((city, date), hour)
    ) WITH CLUSTERING ORDER BY (hour DESC);
    """
    session.execute(query)
    logger.info("Ensured table air_quality_by_city_date exists.")


def _connect_cluster():
    # CASSANDRA_HOSTS can be a comma-separated string or a list
    hosts = CASSANDRA_HOSTS
    if isinstance(hosts, str):
        # allow comma-separated host list in env/config
        hosts = [h.strip() for h in hosts.split(',') if h.strip()]
    return Cluster(contact_points=hosts)


def get_session(retries: int = 12, delay: int = 5):
    """Attempt to connect to Cassandra with retries. Returns an active session.

    Raises the last exception if all retries fail.
    """
    attempt = 0
    last_exception = None

    while attempt < retries:
        attempt += 1
        logger.info(f"Connecting to Cassandra hosts={CASSANDRA_HOSTS} (attempt {attempt}/{retries})")
        cluster = None
        try:
            cluster = _connect_cluster()
            session = cluster.connect()

            # Ensure keyspace and table exist
            create_keyspace(session)
            session.set_keyspace(CASSANDRA_KEYSPACE)
            create_table(session)

            logger.info("Cassandra session established.")
            return session

        except Exception as e:
            last_exception = e
            logger.warning(f"Cassandra not ready (attempt {attempt}/{retries}): {e}")

            # Best-effort shutdown cluster object if created
            try:
                if cluster:
                    cluster.shutdown()
            except Exception:
                pass

            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Exceeded retries connecting to Cassandra. Raising exception.")
                raise last_exception
