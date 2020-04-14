from datetime import datetime, timedelta

import pandas
import pytest

from datalabs.access.sample import SampleFile


def test_standardize(samples):
    standardized_data = SampleFile._standardize(samples)

    # assert 'SOURCE' in standardized_data.columns.values
    # assert 6 == len(standardized_data)
    # assert all(standardized_data['WSLIVE_FILE_DT'].apply(lambda x: hasattr(x, 'tzname')))


@pytest.fixture
def samples():
    return pandas.DataFrame(
        {
            'ME': [1234567, 2345678, 3456789, 4567890],
            'FIRST_NAME': ['Ammar', 'Bob', 'Carol', 'Danielle'],
            'DESCRIPTION': ['Group Practice', 'Group Practice', 'Group Practice', 'Group Practice'],
            'SAMPLE_DATE': [datetime(2019, 10, 22), datetime(2019, 10, 3), datetime(2019, 11, 14),datetime(2019, 12, 9)],
            'SAMPLE_MAX_DATE': [datetime(2019, 12, 22), datetime(2019, 12, 3), datetime(2020, 1, 14),datetime(2020, 2, 9)],
        }
    )
