""" source: datalabs.curate.wslive """
from datetime import datetime

import pandas
import pytest

import datalabs.curate.wslive  # pylint: disable=unused-import


# pylint: disable=redefined-outer-name, protected-access
def test_most_recent_by_me_number(wslive_results):
    filtered_results = wslive_results.wslive._most_recent_by_me_number(wslive_results)

    assert len(filtered_results) == 3
    assert all(filtered_results['PHSYICIAN_FIRST_NAME'] == sorted(filtered_results['PHSYICIAN_FIRST_NAME']))
    assert all(filtered_results['WS_YEAR'] == 2019)
    assert all(filtered_results['WS_MONTH'] == 10)


# pylint: disable=redefined-outer-name
def test_match_to_samples(wslive_results, samples):
    matched_results = wslive_results.wslive.match_to_samples(samples)

    assert len(matched_results) == 3
    assert all(matched_results['PHSYICIAN_FIRST_NAME'] == sorted(matched_results['PHSYICIAN_FIRST_NAME']))
    assert all(matched_results['WS_DATE'] == datetime(2019, 10, 1))
    assert 'DESCRIPTION' in matched_results.columns.values
    assert all(matched_results['DESCRIPTION'] == 'GROUP PRACTICE')


@pytest.fixture
def wslive_results():
    return pandas.DataFrame(
        {
            'PHYSICIAN_ME_NUMBER': [4567890, 2345678, 1234567, 4567890, 2345678, 1234567],
            'PHSYICIAN_FIRST_NAME': ['Danielle', 'Bob', 'Ammar', 'Danielle', 'Bob', 'Ammar'],
            'SOURCE': ['C', 'Z', 'CR', 'C', 'Z', 'CR'],
            'WSLIVE_FILE_DT': [
                datetime(2012, 3, 1), datetime(2014, 4, 1), datetime(2019, 8, 1),
                datetime(2019, 10, 1), datetime(2019, 10, 1), datetime(2019, 10, 1)
            ],
            'WS_YEAR': [2012, 2014, 2019, 2019, 2019, 2019],
            'WS_MONTH': [3, 4, 8, 10, 10, 10],
            'WS_DAY': [1, 1, 1, 1, 1, 1],
            'OFFICE_TELEPHONE': [1, 2, 3, 4, 5, 6],
            'OFFICE_FAX': [1, 2, 3, 4, 5, 6],
            'OFFICE_ADDRESS_LINE_2': [1, 2, 3, 4, 5, 6],
            'OFFICE_ADDRESS_LINE_1': [1, 2, 3, 4, 5, 6],
            'OFFICE_ADDRESS_CITY': [1, 2, 3, 4, 5, 6],
            'OFFICE_ADDRESS_STATE': [1, 2, 3, 4, 5, 6],
            'OFFICE_ADDRESS_ZIP': [1, 2, 3, 4, 5, 6],
            'COMMENTS': [1, 2, 3, 4, 5, 6],
            'SPECIALTY': [1, 2, 3, 4, 5, 6],
            'PRESENT_EMPLOYMENT_CODE': [1, 2, 3, 4, 5, 6],
            'ADDR_STATUS': [1, 2, 3, 4, 5, 6],
            'PHONE_STATUS': [1, 2, 3, 4, 5, 6],
            'FAX_STATUS': [1, 2, 3, 4, 5, 6],
            'SPEC_STATUS': [1, 2, 3, 4, 5, 6],
            'PE_STATUS': [1, 2, 3, 4, 5, 6],
            'NEW_METRIC': [1, 2, 3, 4, 5, 6],
            'PPD_DATE': [1, 2, 3, 4, 5, 6],
        }
    )


@pytest.fixture
def samples():
    return pandas.DataFrame(
        {
            'ME': [1234567, 2345678, 3456789, 4567890],
            'FIRST_NAME': ['Ammar', 'Bob', 'Carol', 'Danielle'],
            'DESCRIPTION': ['GROUP PRACTICE', 'GROUP PRACTICE', 'GROUP PRACTICE', 'GROUP PRACTICE'],
            'SAMPLE_DATE': [
                datetime(2019, 10, 22), datetime(2019, 10, 3), datetime(2019, 11, 14), datetime(2019, 12, 9)
            ],
            'SAMPLE_MAX_DATE': [
                datetime(2019, 12, 22), datetime(2019, 12, 3), datetime(2020, 1, 14), datetime(2020, 2, 9)
            ],
        }
    )
