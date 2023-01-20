""" source: datalabs.etl.orm.provider.mysql """
import logging

import pandas
import pytest

from   datalabs.etl.orm.provider.mysql import ORMLoaderProvider

from   test.datalabs.etl.orm.provider import common  # pylint: disable=wrong-import-order

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# pylint: disable=redefined-outer-name
@pytest.mark.usefixtures("hash_data", "hash_query_results")
def test_generated_row_hashes_match_mysql_hashes(hash_data, hash_query_results):
    common.test_generated_row_hashes_match_dbms_hashes(ORMLoaderProvider(), hash_data, hash_query_results)


# pylint: disable=redefined-outer-name
@pytest.mark.usefixtures("loader_parameters", "table_parameters", "expected_data")
def test_select_new_data(loader_parameters, data, table_parameters, expected_data):
    common.test_select_new_data(ORMLoaderProvider(), loader_parameters, data, table_parameters, expected_data)


# pylint: disable=redefined-outer-name
@pytest.mark.usefixtures("loader_parameters", "table_parameters", "expected_data")
def test_select_deleted_data(loader_parameters, data, table_parameters, expected_data):
    common.test_select_deleted_data(ORMLoaderProvider(), loader_parameters, data, table_parameters, expected_data)


# pylint: disable=redefined-outer-name
@pytest.mark.usefixtures("loader_parameters", "table_parameters", "expected_data")
def test_select_updated_data(loader_parameters, data, table_parameters, expected_data):
    common.test_select_updated_data(ORMLoaderProvider(), loader_parameters, data, table_parameters, expected_data)


@pytest.fixture
def hash_query_results():
    return pandas.DataFrame.from_dict(
        {
            'id': [1, 2, 3, 4],
            'md5': [
                'ee0e5428da3e698ccd3f769599966d79',
                '856595f75daee25c24040759e5aae29d',
                '56bbd2dfb0251e3d1b8266ab9f2ec9cb',
                '8dfb55e8028a88afe6078be695627e73'
            ]
        }
    )


# pylint: disable=blacklisted-name
@pytest.fixture
def expected_data():
    new_data = pandas.DataFrame.from_dict({'dumb': ['grapes'],
                                           'id': [5],
                                           'dumber': ['yum']})

    updated_data = pandas.DataFrame.from_dict({'dumb': ['apples'],
                                               'id': [1],
                                               'dumber': ['good']})

    deleted_data = pandas.DataFrame.from_dict({'id': [4],
                                               'md5': ['8dfb55e8028a88afe6078be695627e73']})

    return {'new': new_data,
            'updated': updated_data,
            'deleted': deleted_data}
