''' Source: datalabs.analysis.amc.address '''
import logging

import pandas
import pytest

from datalabs.analysis.amc.address import AMCAddressFlagger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# def test_good_data(good_data):
#     flagger = AMCAddressFlagger()
#
#     results = flagger.flag(good_data)
#     LOGGER.debug('Good data results: %s', results)
#
#     assert ???
#
#
# def test_bad_data(bad_data):
#     flagger = AMCAddressFlagger()
#
#     results = flagger.flag(bad_data)
#     LOGGER.debug('Bad data results: %s', results)
#
#     assert ???


@pytest.fixture
def good_data():
    return pandas.DataFrame(dict(
            addr_line0=['1234 Foobar St'],
            addr_line1=['Bldg. 56'],
            addr_line2=['Apt. 78'],
            city_cd=['Bismark'],
            state_cd=['ND'],
            zip=['12345'],
            usg_begin_dt=['2018-10-26 12:00 -0530']
        )
    )


@pytest.fixture
def bad_data():
    return pandas.DataFrame(dict(
            addr_line0=['1234 Dumb St'],
            addr_line1=['Bldg. 56'],
            addr_line2=['Apt. 78'],
            city_cd=['Somewhere'],
            state_cd=['ND'],
            zip=['12345'],
            usg_begin_dt=['2018-10-26 12:00 -0530']
        )
    )
