from datetime import datetime, timedelta

import pandas
import pytest

import datalabs.curate.wslive


def test_most_recent_by_me_number(wslive_results):
    standardized_results = wslive_results.wslive.standardize()
    filtered_results = standardized_results.wslive.most_recent_by_me_number()

    assert 3 == len(filtered_results)
    assert all(filtered_results['PHSYICIAN_FIRST_NAME'] == sorted(filtered_results['PHSYICIAN_FIRST_NAME']))
    assert all(2019 == filtered_results['WS_YEAR'])
    assert all(10 == filtered_results['WS_MONTH'])


def test_match_to_samples(wslive_results, samples):
    standardized_results = wslive_results.wslive.standardize()
    matched_results = standardized_results.wslive.match_to_samples(samples)

    assert 3 == len(matched_results)
    assert all(matched_results['PHSYICIAN_FIRST_NAME'] == sorted(matched_results['PHSYICIAN_FIRST_NAME']))
    assert all(datetime(2019, 10, 1) == matched_results['WS_DATE'])
    assert 'DESCRIPTION' in matched_results.columns.values
    assert all('Group Practice' == matched_results['DESCRIPTION'])


@pytest.fixture
def wslive_results():
    return pandas.DataFrame(
        {
            'PHYSICIAN_ME_NUMBER': [4567890, 2345678, 3456789, 1234567, 4567890, 2345678, 3456789, 1234567],
            'PHSYICIAN_FIRST_NAME': ['Danielle', 'Bob', 'Carol', 'Ammar', 'Danielle', 'Bob', 'Carol', 'Ammar'],
            'Source': ['C', 'Z', 'Q', 'CR', 'C', 'Z', 'Q', 'CR'],
            'WSLIVE_FILE_DT': ['3/1/2019', '4/1/2019', '5/1/2018', '8/1/2019', '10/1/2019', '10/1/2019', '10/1/2019', '10/1/2019'],
            'WS_YEAR': [2012, 2014, 2018, 2019, 2019, 2019, 2019, 2019],
            'WS_MONTH': [3, 4, 5, 8, 10, 10, 10, 10],
        }
    )


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
