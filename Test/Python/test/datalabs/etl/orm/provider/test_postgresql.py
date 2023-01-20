""" source: datalabs.etl.orm.provider.postgresql """
import logging

import pandas
import pytest

from   datalabs.etl.orm.provider.postgresql import ORMLoaderProvider

from   test.datalabs.etl.orm.provider import common  # pylint: disable=wrong-import-order

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_row_unquoting():
    csv_string = '"apple pants","1","yummy, yummy","","yip,yip!","chortle"'
    expected_string = '"apple pants",1,"yummy, yummy",,"yip,yip!",chortle'

    quoted_string = ORMLoaderProvider()._standardize_row_text(csv_string)

    assert quoted_string == expected_string


# pylint: disable=redefined-outer-name, protected-access
def test_not_quoting_keywords_columns():
    columns = ['foo', 'primary', 'bar', 'group']
    expected_columns = ['foo', '"primary"', 'bar', '"group"']

    quoted_columns = [ORMLoaderProvider()._quote_keyword(column) for column in columns]

    assert quoted_columns == expected_columns


# pylint: disable=redefined-outer-name
@pytest.mark.usefixtures("hash_data", "hash_query_results")
def test_generated_row_hashes_match_postgres_hashes(hash_data, hash_query_results):
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
                '25a93a044406f7d9d3d7a5c98bb9dd1a',
                '5bdf77504ce234e0968bef50b65d5737',
                '5bffaf8d5a76dd29c65ca75e690ce459',
                '6a2b0a91ec079894f7a6b3e933f216fe'
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
                                               'md5': ['6a2b0a91ec079894f7a6b3e933f216fe']})

    return {'new': new_data,
            'updated': updated_data,
            'deleted': deleted_data}
