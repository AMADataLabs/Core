""" source: datalabs.access.wslive """
from datetime import datetime

import pandas
import pytest

from datalabs.access.wslive import WSLiveFile


# pylint: disable=redefined-outer-name,protected-access
def test_standardize(wslive_results):
    data_date = datetime(1912, 12, 19)
    standardized_data = WSLiveFile._standardize(wslive_results, data_date)

    assert 'SOURCE' in standardized_data.columns.values
    assert 'BOGUS_COLUMN' not in standardized_data.columns.values
    assert len(standardized_data) == 6
    assert all(standardized_data['WSLIVE_FILE_DT'].apply(lambda x: hasattr(x, 'tzname')))


@pytest.fixture
def wslive_results():
    return pandas.DataFrame(
        {
            'PHYSICIAN_ME_NUMBER': [4567890, 2345678, 3456789, 1234567, 4567890, 2345678, 3456789, 1234567],
            'PHSYICIAN_FIRST_NAME': ['Danielle', 'Bob', 'Carol', 'Ammar', 'Danielle', 'Bob', 'Carol', 'Ammar'],
            'Source': ['C', 'Z', 'Q', 'CR', 'C', 'Z', 'Q', 'CR'],
            'WSLIVE_FILE_DT': [
                '3/1/2019', '4/1/2019', '5/1/2018', '8/1/2019', '10/1/2019', '10/1/2019', '10/1/2019', '10/1/2019'
            ],
            'WS_YEAR': [2012, 2014, 2018, 2019, 2019, 2019, 2019, 2019],
            'WS_MONTH': [3, 4, 5, 8, 10, 10, 10, 10],
            'OFFICE_TELEPHONE': [1, 2, 3, 4, 5, 6, 7, 8],
            'OFFICE_FAX': [1, 2, 3, 4, 5, 6, 7, 8],
            'OFFICE_ADDRESS_LINE_2': [1, 2, 3, 4, 5, 6, 7, 8],
            'OFFICE_ADDRESS_LINE_1': [1, 2, 3, 4, 5, 6, 7, 8],
            'OFFICE_ADDRESS_CITY': [1, 2, 3, 4, 5, 6, 7, 8],
            'OFFICE_ADDRESS_STATE': [1, 2, 3, 4, 5, 6, 7, 8],
            'OFFICE_ADDRESS_ZIP': [1, 2, 3, 4, 5, 6, 7, 8],
            'COMMENTS': [1, 2, 3, 4, 5, 6, 7, 8],
            'SPECIALTY': [1, 2, 3, 4, 5, 6, 7, 8],
            'PRESENT_EMPLOYMENT_CODE': [1, 2, 3, 4, 5, 6, 7, 8],
            'ADDR_STATUS': [1, 2, 3, 4, 5, 6, 7, 8],
            'PHONE_STATUS': [1, 2, 3, 4, 5, 6, 7, 8],
            'FAX_STATUS': [1, 2, 3, 4, 5, 6, 7, 8],
            'SPEC_STATUS': [1, 2, 3, 4, 5, 6, 7, 8],
            'PE_STATUS': [1, 2, 3, 4, 5, 6, 7, 8],
            'NEW_METRIC': [1, 2, 3, 4, 5, 6, 7, 8],
            'PPD_DATE': [1, 2, 3, 4, 5, 6, 7, 8],
            'BOGUS_COLUMN': [1, 2, 3, 4, 5, 6, 7, 8],
        }
    )
