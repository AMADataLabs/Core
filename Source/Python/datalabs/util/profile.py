''' Performance profiling utilities. '''
from   datetime import datetime
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def run_time_logger(func):
    def wrapper(*args, **kwargs):
        start = datetime.now().isoformat()
        LOGGER.info(f"start: {start} @{func.__name__}")

        result = func(*args, **kwargs)

        end = datetime.now().isoformat()
        LOGGER.info(f"end: {end} @{func.__name__}")

        return result

    return wrapper
