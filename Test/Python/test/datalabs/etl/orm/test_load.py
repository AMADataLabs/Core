""" source: datalabs.etl.orm.load """
import logging
import tempfile

import mock
import pandas
import pytest

from   datalabs.access.orm import Database
from   datalabs.etl.orm.load import ORMLoaderTask
import datalabs.etl.task as task

from   test.datalabs.access.model import Base  # pylint: disable=wrong-import-order

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_orm_loader(components):
    with mock.patch('datalabs.etl.orm.load.Database'):
        loader = ORMLoaderTask(components)
        loader._load()


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def components(database, file, data):
    return dict(
        TASK_CLASS='datalabs.etl.orm.loader.ORMLoaderTask',
        MODEL_CLASSES='test.datalabs.access.model.Foo,'
                      'test.datalabs.access.model.Bar,'
                      'test.datalabs.access.model.Poof',
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

    return list([pandas.DataFrame.from_dict(data).to_csv() for data in (foo, bar, poof)])


@pytest.fixture
def file():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as database_file:
        yield database_file.name


# pylint: disable=redefined-outer-name
@pytest.fixture
def parameters(file):
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
def database(parameters):
    with Database.from_parameters(parameters) as database:
        Base.metadata.create_all(database._connection.get_bind())

        yield database
