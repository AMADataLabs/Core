""" source: datalabs.etl.orm.load """
import logging
import tempfile

import mock
import pandas
import pytest

from   datalabs.access.orm import Database
from   datalabs.etl.orm.load import ORMLoaderTask

from   test.datalabs.access.model import Base  # pylint: disable=wrong-import-order

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_orm_loader(loader_parameters):
    with mock.patch('datalabs.etl.orm.load.Database'):
        loader = ORMLoaderTask(loader_parameters)
        loader._load()


# pylint: disable=redefined-outer-name, protected-access
def test_generated_row_hashes_match_postgres_hashes(loader_parameters, hash_data, hash_query_results):
    columns = ['dumb', 'id', 'dumber']
    loader = ORMLoaderTask(loader_parameters)
    row_hashes = loader._generate_row_hashes(hash_data, columns)

    for generated_hash, db_hash in zip(row_hashes, hash_query_results['md5']):
        assert generated_hash == db_hash


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
        TASK_CLASS='datalabs.etl.orm.loader.ORMLoaderTask',
        MODEL_CLASSES='test.datalabs.access.model.Foo,'
                      'test.datalabs.access.model.Bar,'
                      'test.datalabs.access.model.Poof',
        TABLES='foo,'
               'bar,'
               'poof',
        thing=True,
        DATABASE_BACKEND='sqlite',
        DATABASE_NAME=file,
        DATABASE_HOST='',
        DATABASE_PORT='',
        DATABASE_USERNAME='',
        DATABASE_PASSWORD='',
        data=data
    )


# pylint: disable=blacklisted-name
@pytest.fixture
def hash_data():
    data = {'dumb': ['apple', 'oranges', 'bananas'], 'id': [1, 2, 3], 'dumber': ['good', 'yummy', 'bad']}

    return pandas.DataFrame.from_dict(data)


@pytest.fixture
def hash_query_results():
    return pandas.DataFrame.from_dict(
        {
            'id': [1, 2, 3],
            'md5': [
                'a0c4bd642e6d37a35dcca8a9e0d5ab43',
                '0225525e6052c8be174995150a302e60',
                '1409af11b29204e49ca9b8fe834b8270'
            ]
        }
    )
