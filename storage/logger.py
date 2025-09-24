import logging
import sys

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger