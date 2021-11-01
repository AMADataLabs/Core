""" source: datalabs.etl.orm.load """
import logging
import tempfile

import mock
import pandas
import pytest

from   datalabs.access.orm import Database
from   datalabs.etl.orm.load import ORMLoaderTask
from   datalabs.etl.orm.load import TableParameters

from   test.datalabs.access.model import Base  # pylint: disable=wrong-import-order

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.mark.skip(reason="Need data from database")
# pylint: disable=redefined-outer-name, protected-access
def test_orm_loader(loader_parameters):
    with mock.patch('datalabs.etl.orm.load.Database'):
        loader = ORMLoaderTask(loader_parameters)
        loader._load()


# pylint: disable=redefined-outer-name, protected-access
def test_row_unquoting():
    csv_string = '"apple pants","1","yummy, yummy","","yip,yip!","chortle"'
    expected_string = '"apple pants",1,"yummy, yummy","","yip,yip!",chortle'

    quoted_string = ORMLoaderTask._standardize_row_text(csv_string)

    assert quoted_string == expected_string


# pylint: disable=redefined-outer-name, protected-access
def test_not_unquoting_keywords():
    csv_string = '"foo","primary","bar"'
    expected_string = 'foo,"primary",bar'

    quoted_string = ORMLoaderTask._standardize_row_text(csv_string)

    assert quoted_string == expected_string


# pylint: disable=redefined-outer-name, protected-access
def test_generated_row_hashes_match_postgres_hashes(loader_parameters, hash_data, hash_query_results):
    columns = ['dumb', 'id', 'dumber']
    loader = ORMLoaderTask(loader_parameters)
    primary_key = 'id'
    row_hashes = loader._generate_row_hashes(hash_data, primary_key, columns)

    for generated_hash, db_hash in zip(row_hashes['md5'], hash_query_results['md5']):
        assert generated_hash == db_hash


# pylint: disable=redefined-outer-name, protected-access
def test_select_new_data(loader_parameters, table_parameters, expected_data):
    loader = ORMLoaderTask(loader_parameters)

    row_hashes = loader._generate_row_hashes(
        table_parameters.data,
        table_parameters.primary_key,
        table_parameters.columns
    )
    table_parameters.incoming_hashes = row_hashes

    new_data = loader._select_new_data(table_parameters)

    assert expected_data['new'].equals(new_data)


# pylint: disable=redefined-outer-name, protected-access
def test_select_deleted_data(loader_parameters, table_parameters, expected_data):
    loader = ORMLoaderTask(loader_parameters)

    row_hashes = loader._generate_row_hashes(
        table_parameters.data,
        table_parameters.primary_key,
        table_parameters.columns
    )
    table_parameters.incoming_hashes = row_hashes

    deleted_data = loader._select_deleted_data(table_parameters)

    assert expected_data['deleted'].equals(deleted_data)


def test_select_updated_data(loader_parameters, table_parameters, expected_data):
    loader = ORMLoaderTask(loader_parameters)

    row_hashes = loader._generate_row_hashes(
        table_parameters.data,
        table_parameters.primary_key,
        table_parameters.columns
    )
    table_parameters.incoming_hashes = row_hashes

    updated_data = loader._select_updated_data(table_parameters)

    assert expected_data['updated'].equals(updated_data)


# pylint: disable=protected-access
def test_get_schema_from_dict_table_args():
    class MockObject:
        __table_args__ = {"schema": "ormloader"}

    schema = ORMLoaderTask._get_schema(MockObject)

    assert schema == "ormloader"


# pylint: disable=protected-access
def test_get_schema_from_tuple_table_args():
    class MockObject:
        __table_args__ = (42, {"stuff": "jfdi9049d0sjafe"}, {"schema": "ormloader"})

    schema = ORMLoaderTask._get_schema(MockObject)

    assert schema == "ormloader"


# pylint: disable=blacklisted-name
@pytest.fixture
def data():
    foo = dict(
        this={0: 'ping', 1: 'pang', 2: 'pong'},
        that={0: 'biff', 1: 'baff', 2: 'buff'},
    )

    bar = dict(
        one={0: 11, 1: 42},
        two={0: 'swish', 1: 'swash'}
    )

    poof = dict(
        a={0: 30},
        b={0: True}
    )

    return list(pandas.DataFrame.from_dict(data).to_csv().encode('utf-8', errors='backslashreplace')
                for data in (foo, bar, poof))


@pytest.fixture
def file():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as database_file:
        yield database_file.name


# pylint: disable=redefined-outer-name
@pytest.fixture
def database_parameters(file):
    return dict(
        backend='sqlite',
        name=file,
        host='',
        port='',
        username='',
        password=''
    )


# pylint: disable=redefined-outer-name, protected-access
@pytest.fixture
def database(database_parameters):
    with Database.from_parameters(database_parameters) as database:
        Base.metadata.create_all(database._connection.get_bind())

        yield database


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def loader_parameters(database, file, data):
    return dict(
        # TASK_CLASS='datalabs.etl.orm.loader.ORMLoaderTask',
        MODEL_CLASSES='test.datalabs.access.model.Foo,'
                      'test.datalabs.access.model.Bar,'
                      'test.datalabs.access.model.Poof',
        DATABASE_HOST='',
        DATABASE_PORT='',
        DATABASE_BACKEND='sqlite',
        DATABASE_NAME=file,
        DATABASE_USERNAME='',
        DATABASE_PASSWORD='',
        data=data
    )


# pylint: disable=blacklisted-name
@pytest.fixture
def hash_data():
    data = {
        'dumb': ['apple pants', 'oranges', 'nectarines', 'bananas'],
        'id': [1, 2, 3, 4],
        'dumber': ['good', 'yummy, yummy', '', 'bad']
    }

    return pandas.DataFrame.from_dict(data)


@pytest.fixture
def hash_query_results():
    return pandas.DataFrame.from_dict(
        {
            'id': [1, 2, 3, 4],
            'md5': [
                '25a93a044406f7d9d3d7a5c98bb9dd1a',
                '5bdf77504ce234e0968bef50b65d5737',
                '2611193cbb903e5ae23a7be15ca749d8',
                '6a2b0a91ec079894f7a6b3e933f216fe'
            ]
        }
    )


# pylint: disable=blacklisted-name
@pytest.fixture
def incoming_data():
    data = {
        'dumb': ['apples', 'oranges', 'nectarines', 'grapes'],
        'id': [1, 2, 3, 5],
        'dumber': ['good', 'yummy, yummy', '', 'yum']
    }

    return pandas.DataFrame.from_dict(data)


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


@pytest.fixture
def table_parameters(incoming_data, hash_query_results):
    data = incoming_data
    model_class = 'test.datalabs.access.model.Foo'
    primary_key = 'id'
    columns = ['dumb', 'id', 'dumber']
    current_hashes = hash_query_results
    incoming_hashes = None

    table_parameters = TableParameters(data, model_class, primary_key, columns, current_hashes, incoming_hashes)

    return table_parameters
