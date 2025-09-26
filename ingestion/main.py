from scheduler import start_scheduler, run_backfill
import logging
import sys
from metrics import start_metrics_server

def setup_logging():
    """Setup structured logging with proper formatting"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/logs/ingestion.log', mode='a')
        ]
    )
    
    # Set specific loggers to appropriate levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    return logger

if __name__ == '__main__':
    logger = setup_logging()
    logger.info("Starting Air Quality Ingestion Service")
    
    try:
        # Start metrics server
        start_metrics_server(8000)
        logger.info("Metrics server started on port 8000")
        
        # Run backfill
        logger.info("Starting backfill process")
        run_backfill()
        logger.info("Backfill process completed")
        
        # Start scheduler
        logger.info("Starting scheduled processing")
        start_scheduler()
        
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed with error: {str(e)}")
        sys.exit(1)
    