""" source: datalabs.access.sample """
from datetime import datetime

import pandas
import pytest

from datalabs.access.sample import SampleFile


# pylint: disable=redefined-outer-name,protected-access
def test_standardize(samples):
    data_date = datetime(1912, 12, 19)
    max_date = datetime(1913, 2, 19)
    standardized_data = SampleFile._standardize(samples, data_date)

    assert all(data_date == standardized_data['SAMPLE_DATE'])
    assert all(max_date == standardized_data['SAMPLE_MAX_DATE'])


@pytest.fixture
def samples():
    return pandas.DataFrame(
        {
            'ME': [1234567, 2345678, 3456789, 4567890],
            'FIRST_NAME': ['Ammar', 'Bob', 'Carol', 'Danielle'],
            'DESCRIPTION': ['Group Practice', 'Group Practice', 'Group Practice', 'Group Practice'],
            'SAMPLE_DATE': [
                datetime(2019, 10, 22), datetime(2019, 10, 3), datetime(2019, 11, 14), datetime(2019, 12, 9)
            ],
            'SAMPLE_MAX_DATE': [
                datetime(2019, 12, 22), datetime(2019, 12, 3), datetime(2020, 1, 14), datetime(2020, 2, 9)
            ],
        }
    )
