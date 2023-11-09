""" datetime helper functions """
from datetime import datetime


def get_current_datetime():
    current_date_time = datetime.now()
    current_date_time_str = current_date_time.strftime("%Y%m%d%H%M%S")

    return current_date_time_str
