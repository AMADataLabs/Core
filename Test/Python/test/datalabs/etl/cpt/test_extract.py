""" source: datalabs.etl.cpt.extract """
from datetime import date
import json
import logging

import mock
import pytest

from   datalabs.etl.cpt.extract import CPTTextDataExtractor

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_datestamp_conversion():
    datestamps = ['1-Jan', '15-Dec', '13-Mar']
    expected_dates = [date(1900, 1, 1), date(1900, 12, 15), date(1900, 3, 13)]
    dates = CPTTextDataExtractor._convert_datestamps_to_dates(datestamps)

    for expected_date, actual_date in zip(expected_dates, dates):
        assert actual_date == expected_date


@mock.patch('datalabs.etl.cpt.extract.CPTTextDataExtractor._get_latest_path')
def test_extract_release_date(get_latest_path):
    get_latest_path.return_value = 'AMA/CPT/20200131'
    extractor = CPTTextDataExtractor(None)
    expected_release_date = date(2020, 1, 31)
    release_date = extractor._extract_release_date()

    assert get_latest_path.call_count == 1
    assert release_date == expected_release_date

def test_generate_release_types(release_schedule):
    extractor = CPTTextDataExtractor(dict(RELEASE_SCHEDULE=json.dumps(release_schedule)))
    release_types = extractor._generate_release_types(release_schedule)

    assert len(release_types.columns.values) == 1
    assert 'type' in release_types
    assert len(release_types) == 6
    assert release_types.type.to_list() == ['ANNUAL', 'Q1', 'Q2', 'Q3', 'Q4', 'OTHER']

def test_get_release_type(release_schedule):
    extractor = CPTTextDataExtractor(dict(RELEASE_SCHEDULE=json.dumps(release_schedule)))
    release_date = date(2020, 7, 1)
    expected_release_type = 'Q3'
    release_type = extractor._get_release_type(release_schedule, release_date)

    assert release_type == expected_release_type



@pytest.fixture
def release_schedule():
    return {
        "ANNUAL": ["1-Sep", "1-Jan"],
        "Q1": ["1-Jan", "1-Apr"],
        "Q2": ["1-Apr", "1-Jul"],
        "Q3": ["1-Jul", "1-Oct"],
        "Q4": ["1-Oct", "1-Jan"]
    }
