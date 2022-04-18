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

    assert all(c in standardized_data.columns.values for c in ['SAMPLE_DATE', 'SAMPLE_MAX_DATE'])
    assert all(data_date == standardized_data['SAMPLE_DATE'])
    assert all(max_date == standardized_data['SAMPLE_MAX_DATE'])


@pytest.fixture
def samples():
    return pandas.DataFrame(
        {
            'ME': [7654321, 8765432, 9876543, 987654],
            'FIRST_NAME': ['Amy', 'Bill', 'Caroline', 'Doug'],
            'DESCRIPTION': ['NO CLASSIFICATION', 'NO CLASSIFICATION', 'NO CLASSIFICATION', 'NO CLASSIFICATION'],
        }
    )
