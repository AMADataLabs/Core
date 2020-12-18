""" source: datalabs.etl.orm.load """
import logging
import tempfile

import pandas
import pytest

from   datalabs.access.orm import Database
from   datalabs.access.orm import DatabaseTaskMixin
from   datalabs.etl.orm.load import ORMLoaderTask
import datalabs.etl.task as task

from   test.datalabs.access.model import Base, Foo, Bar, Poof

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_orm_loader(components):
    loader = ORMLoaderTask(components)
    loader._load()

    mixin = DatabaseTaskMixin()
    with mixin._get_database(components.database) as database:
        foos = database.query(Foo).all()
        assert len(foos) == 3
        assert foos[0].this == 'ping'
        assert foos[2].that == 'buff'

        bars = database.query(Bar).all()
        assert len(bars) == 2
        assert bars[0].one == 11
        assert bars[1].two == 'swash'

        poofs = database.query(Poof).all()
        assert len(poofs) == 1
        assert poofs[0].a == 30
        assert poofs[0].b


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def components(database, file, data):
    return task.ETLComponentParameters(
        database=dict(
            backend='sqlite',
            name=file,
            host='',
            port='',
            username='',
            password=''
        ),
        variables=dict(
            CLASS='datalabs.etl.orm.loader.ORMLoaderTask',
            MODELCLASSES='test.datalabs.access.model.Foo,test.datalabs.access.model.Bar,test.datalabs.access.model.Poof',
            thing=True,
        ),
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
