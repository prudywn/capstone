from scheduler import start_scheduler, run_backfill
import logging
from metrics import start_metrics_server

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    start_metrics_server(8000)
    run_backfill() # catch up on past data
    start_scheduler() # start hourly scheduled polling
    