import logging
import os
import tempfile

import pandas
import pytest
import sqlalchemy as sa
from   sqlalchemy.ext.declarative import declarative_base
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.database import Database

from   test.datalabs.access.model import Base, Foo, Bar, Pow

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


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
    class SQLAlchemyDatabase(Database):
        def connect(self):
            engine = sa.create_engine(self.url, echo=True)
            Session = sessionmaker(bind=engine)

            self._connection = Session()

        def add(self, model, **kwargs):
            self._connection.add(model)

        def commit(self):
            self._connection.commit()


    db = SQLAlchemyDatabase.from_parameters(parameters)
    with db:
        Base.metadata.create_all(db._connection.get_bind())

        yield db


def test_adding_objects(database, file):

    models = [
        Foo(this='ping', that='biff'),
        Foo(this='pang', that='baff'),
        Foo(this='pong', that='buff'),
        Bar(one=11, two='swish'),
        Bar(one=42, two='swish'),
        Pow(a=30, b=True),
    ]

    for model in models:
        database.add(model)

    database.commit()

    engine = sa.create_engine(f'sqlite:///{file}', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    foos = session.query(Foo).all()
    LOGGER.debug('Foos: %s', foos)
    assert len(foos) == 3

    bars = session.query(Bar).all()
    LOGGER.debug('Bars: %s', bars)
    assert len(bars) == 2

    pows = session.query(Pow).all()
    LOGGER.debug('Pows: %s', pows)
    assert len(pows) == 1
