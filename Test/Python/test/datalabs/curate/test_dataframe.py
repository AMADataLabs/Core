""" source: datalabs.curate.dataframe """
import pandas
import pytest

import datalabs.curate.dataframe  # pylint: disable=unused-import


# pylint: disable=redefined-outer-name
def test_rename_in_upper_case(data):
    data = data.datalabs.rename_in_upper_case()

    assert all([c in data.columns.values for c in ['FILIBUSTER', 'PANDEMIC']])


# pylint: disable=redefined-outer-name
def test_upper(data):
    data = data.datalabs.upper()

    assert all([v in data['filibuster'].values for v in ['FANBOY', 'FORTITUDE']])


# pylint: disable=redefined-outer-name
def test_strip(data):
    data = data.datalabs.strip()

    assert all([c in data['pandemic'].values for c in ['platitude', 'pragmatism']])


@pytest.fixture
def data():
    return pandas.DataFrame({'filibuster': ['fanboy', 'fortitude'], 'pandemic': ['  platitude ', ' pragmatism     ']})
