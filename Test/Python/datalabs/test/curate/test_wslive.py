import pandas
import pytest

import datalabs.curate.wslive


def test_standardize(wslive_results):
    standardized_results = wslive_results.wslive.standardize()

    assert 'SOURCE' in standardized_results.columns.values
    assert 6 == len(standardized_results)
    assert all(standardized_results['WSLIVE_FILE_DT'].apply(lambda x: hasattr(x, 'tzname')))


def test_most_recent_by_me_number(wslive_results):
    standardized_results = wslive_results.wslive.standardize()
    filtered_results = standardized_results.wslive.most_recent_by_me_number()

    assert 3 == len(filtered_results)
    assert all(filtered_results['PHSYICIAN_FIRST_NAME'] == sorted(filtered_results['PHSYICIAN_FIRST_NAME']))
    assert all(2019 == filtered_results['WS_YEAR'])
    assert all(10 == filtered_results['WS_MONTH'])


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