""" source: datalabs.etl.cpt.extract """
from datetime import date
import logging

import mock

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
