''' Source: datalabs.analysis.amc.transform '''
import logging

import pandas
import pytest

from datalabs.analysis.amc.transform import AMCAddressFlaggingTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# def test_good_data(good_data):
#     transformer = AMCAddressFlaggingTransformerTask(dict(
#             data=good_data
#         )
#     )
#
#     results = transformer.run()
#     LOGGER.debug('Good data results: %s', results)
#
#     assert ???
#
#
# def test_bad_data(bad_data):
#     transformer = AMCAddressFlaggingTransformerTask(dict(
#             data=bad_data
#         )
#     )
#
#     results = transformer.run()
#     LOGGER.debug('Bad data results: %s', results)
#
#     assert ???


@pytest.fixture
def good_data():
    return '''addr_line0,addr_line1,addr_line2,city_cd,state_cd,zip,usg_begin_dt
1234 Foobar St,Bldg. 56,Apt. 78,Bismark,ND,12345,2018-10-26 12:00 -0530
1234 Pickle Dr,Bldg. 12,Apt. 45,Sycamore,IL,60178,2021-12-02 15:00 -0700'''


@pytest.fixture
def bad_data():
    return '''addr_line0,addr_line1,addr_line2,city_cd,state_cd,zip,usg_begin_dt
1234 Dumb St,Bldg. 56,Apt. 78,Somewhere,ND,12345,2018-10-26 12:00 -0530
1234 Stupid St,Bldg. 56,Apt. 78,Anywhere,ND,12345,2018-10-26 12:00 -0530'''
