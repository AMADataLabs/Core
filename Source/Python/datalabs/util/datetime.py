""" Date/time utility functions.  """
import calendar
from datetime import datetime


def date_range(start_date_str, end_date_str):
    start_date = _parse_date(start_date_str, default_day=1)
    end_date = _parse_date(end_date_str)
    current_date = datetime.now()

    if end_date > current_date:
        end_date = datetime(current_date.year, current_date.month, current_date.day)

    date_range_str = '{}_to_{}'.format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    return start_date, end_date, date_range_str


def _parse_date(date_str, default_day=None):
    date = None

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as error:
        if 'does not match format' not in error.args[0]:
            raise error

    if not date:
        date = _parse_partial_date(date_str, default_day)

    return date


def _parse_partial_date(date_str, default_day):
    date = datetime.strptime(date_str, '%Y-%m')

    if not default_day:
        default_day = calendar.monthrange(date.year, date.month)[1]

    return datetime(date.year, date.month, default_day)
