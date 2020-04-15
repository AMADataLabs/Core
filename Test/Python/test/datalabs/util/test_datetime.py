""" source: datalabs.util.datetime """
from datetime import datetime
from collections import namedtuple

import pytest

import datalabs.util.datetime as dt


DateData = namedtuple('DateData', 'start_str start end_str end range')


# pylint: disable=redefined-outer-name
def test_full_date_range(date_test_data):
    _test_date_range(date_test_data['full'])


# pylint: disable=redefined-outer-name
def test_partial_date_range(date_test_data):
    _test_date_range(date_test_data['partial'])


# pylint: disable=redefined-outer-name
def test_future_full_date_range(date_test_data):
    _test_date_range(date_test_data['future_full'])


# pylint: disable=redefined-outer-name
def test_future_partial_date_range(date_test_data):
    _test_date_range(date_test_data['future_partial'])


# pylint: disable=redefined-outer-name
def _test_date_range(data):
    start_date, end_date, date_range_str = dt.date_range(data.start_str, data.end_str)

    assert data.start == start_date
    assert data.end == end_date
    assert data.range == date_range_str


@pytest.fixture
def date_test_data():
    current_date = datetime.now()
    current_date = datetime(current_date.year, current_date.month, current_date.day)
    current_date_str = current_date.strftime('%Y-%m-%d')

    return dict(
        full=DateData(
            '1970-01-15', datetime(1970, 1, 15,),
            '1980-11-05', datetime(1980, 11, 5),
            '1970-01-15_to_1980-11-05'
        ),
        partial=DateData(
            '1970-01', datetime(1970, 1, 1,),
            '2020-03', datetime(2020, 3, 31),
            '1970-01-01_to_2020-03-31'
        ),
        future_full=DateData(
            '2020-01-15', datetime(2020, 1, 15,),
            '4040-11-05', current_date,
            f'2020-01-15_to_{current_date_str}'
        ),
        future_partial=DateData(
            '2020-01', datetime(2020, 1, 1,),
            '4040-11', current_date,
            f'2020-01-01_to_{current_date_str}'
        ),
    )
