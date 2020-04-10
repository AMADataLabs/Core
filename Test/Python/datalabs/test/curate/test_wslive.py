import pandas
import pytest

import datalabs.curate.wslive


def test_standardize(wslive_results):
    standardized_results = wslive_results.wslive.standardize()

    assert 'SOURCE' in standardized_results.columns.values
    assert len(standardized_results) == len(wslive_results) - 2
    assert all(standardized_results['WSLIVE_FILE_DT'].apply(lambda x: hasattr(x, 'tzname')))


@pytest.fixture
def wslive_results():
    return pandas.DataFrame(
        {
            'PHYSICIAN_ME_NUMBER': [1234567, 2345678, 3456789, 4567890, 1234567, 2345678, 3456789, 4567890],
            'PHSYICIAN_FIRST_NAME': ['Patricia', 'Bob', 'Terry', 'Omar', 'Patricia', 'Bob', 'Terry', 'Omar'],
            'Source': ['C', 'Z', 'Q', 'CR', 'C', 'Z', 'Q', 'CR'],
            'WSLIVE_FILE_DT': ['3/1/2019', '4/1/2019', '5/1/2018', '8/1/2019', '10/1/2019', '10/1/2019', '10/1/2019', '10/1/2019'],
            'WS_YEAR': [2012, 2014, 2018, 2019, 2019, 2019, 2019, 2019],
            'WS_MONTH': [3, 4, 5, 8, 10, 10, 10, 10],
        }
    )