""" ORM loader task tests """
import logging
import os
import tempfile

import pandas
import pytest
import sqlalchemy
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.orm import Database
from   datalabs.access.orm import DatabaseTaskMixin
from   datalabs.etl.orm.load import ORMLoaderTask
import datalabs.etl.task as task
# import datalabs.model.masterfile.oneview as dbmodel
from   test.datalabs.access.model import Base, Foo, Bar, Pow

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# @pytest.mark.skip(reason="Integration test.")
def test_orm_loader(database, file, components):
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

        pows = database.query(Pow).all()
        assert len(pows) == 1
        assert pows[0].a == 30
        assert pows[0].b


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
            MODELCLASSES='test.datalabs.access.model.Foo,test.datalabs.access.model.Bar,test.datalabs.access.model.Pow',
            thing=True,
        ),
        data=data
    )


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

    pow = dict(
        a={0: 30},
        b={0: True}
    )

    return list([pandas.DataFrame.from_dict(data).to_csv() for data in (foo, bar, pow)])


@pytest.fixture
def file():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as database_file:
        yield database_file.name


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


@pytest.fixture
def database(parameters):
    with Database.from_parameters(parameters) as db:
        Base.metadata.create_all(db._connection.get_bind())

        yield db
